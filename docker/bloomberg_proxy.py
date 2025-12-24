from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import httpx
import os
from datetime import datetime

app = FastAPI(title="Bloomberg News Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "bloomberg-real-time.p.rapidapi.com"
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")

headers = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY,
}

# Widget configuration for OpenBB Workspace - using markdown for clickable links
WIDGETS_CONFIG = {
    "bloomberg_terminal_markets": {
        "name": "Bloomberg Terminal - Markets",
        "description": "Bloomberg Terminal style news feed - Markets",
        "category": "News",
        "type": "markdown",
        "searchCategory": "News",
        "endpoint": "news/markdown",
        "widgetId": "bloomberg_terminal_markets",
        "params": [
            {
                "paramName": "category",
                "label": "Category",
                "type": "form",
                "value": "markets",
                "description": "News category"
            }
        ],
        "source": ["Bloomberg"],
        "refetchInterval": 60000
    },
    "bloomberg_terminal_tech": {
        "name": "Bloomberg Terminal - Technology",
        "description": "Bloomberg Terminal style news feed - Technology",
        "category": "News",
        "type": "markdown",
        "searchCategory": "News",
        "endpoint": "news/markdown",
        "widgetId": "bloomberg_terminal_tech",
        "params": [
            {
                "paramName": "category",
                "label": "Category",
                "type": "form",
                "value": "technology",
                "description": "News category"
            }
        ],
        "source": ["Bloomberg"],
        "refetchInterval": 60000
    },
    "bloomberg_terminal_politics": {
        "name": "Bloomberg Terminal - Politics",
        "description": "Bloomberg Terminal style news feed - Politics",
        "category": "News",
        "type": "markdown",
        "searchCategory": "News",
        "endpoint": "news/markdown",
        "widgetId": "bloomberg_terminal_politics",
        "params": [
            {
                "paramName": "category",
                "label": "Category",
                "type": "form",
                "value": "politics",
                "description": "News category"
            }
        ],
        "source": ["Bloomberg"],
        "refetchInterval": 60000
    },
    "bloomberg_terminal_all": {
        "name": "Bloomberg Terminal - All News",
        "description": "Full Bloomberg Terminal experience in iframe",
        "category": "News",
        "type": "markdown",
        "searchCategory": "News",
        "endpoint": "news/iframe",
        "widgetId": "bloomberg_terminal_all",
        "params": [],
        "source": ["Bloomberg"],
        "refetchInterval": 300000
    }
}

@app.get("/widgets.json")
async def get_widgets():
    return JSONResponse(content=WIDGETS_CONFIG)

@app.get("/health")
async def health():
    return {"status": "ok"}

def format_timestamp(ts):
    """Convert Unix timestamp to readable time"""
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("%H:%M")
    except:
        return ""

@app.get("/stories/list")
async def get_stories_list(id: str = Query("markets", description="Category (not used - returns all latest news)")):
    """Get stories/news - formatted for Bloomberg Terminal style"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/news/list",
            headers=headers,
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        
        # Extract stories from all modules in the new API format
        all_stories = []
        if data.get("status") and data.get("data"):
            modules = data["data"].get("modules", [])
            for module in modules:
                stories = module.get("stories", [])
                all_stories.extend(stories)
        
        # Deduplicate by ID
        seen_ids = set()
        unique_items = []
        for item in all_stories:
            item_id = item.get("id", item.get("internalID", item.get("title", "")))
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_items.append(item)
        
        # Sort by timestamp descending (newest first)
        unique_items.sort(key=lambda x: x.get("published", 0), reverse=True)
        
        # Filter by category if specified (client-side filtering)
        category_map = {
            "markets": ["markets", "stocks", "currencies"],
            "technology": ["technology", "tech"],
            "politics": ["politics", "government"],
            "industries": ["industries", "energy", "health"],
            "wealth": ["wealth", "personal-finance"]
        }
        
        if id.lower() in category_map:
            allowed = category_map[id.lower()]
            unique_items = [item for item in unique_items 
                          if item.get("primarySite", "").lower() in allowed 
                          or any(a in item.get("primarySite", "").lower() for a in allowed)]
        
        formatted_results = []
        for item in unique_items[:20]:
            # Parse Unix timestamp
            published = item.get("published", 0)
            time_str = format_timestamp(published) if published else ""
            
            formatted_results.append({
                "time": time_str,
                "headline": item.get("title", item.get("headline", "")),
                "category": item.get("primarySite", "NEWS").upper(),
                "url": item.get("url", item.get("shortURL", "")),
                "thumbnail": item.get("thumbnailImage", item.get("image", ""))
            })
        
        return {
            "results": formatted_results,
            "provider": "bloomberg",
            "warnings": None,
            "chart": None,
            "extra": {"metadata": {"route": "/stories/list", "count": len(formatted_results)}}
        }

@app.get("/news/markdown")
async def get_news_markdown(category: str = Query("markets", description="Category (returns all latest news)")):
    """Get news formatted as markdown with clickable links - Bloomberg Terminal style"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/news/list",
            headers=headers,
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        
        # Extract stories from all modules
        all_stories = []
        if data.get("status") and data.get("data"):
            modules = data["data"].get("modules", [])
            for module in modules:
                stories = module.get("stories", [])
                all_stories.extend(stories)
        
        # Deduplicate and sort
        seen_ids = set()
        unique_items = []
        for item in all_stories:
            item_id = item.get("id", item.get("internalID", item.get("title", "")))
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_items.append(item)
        unique_items.sort(key=lambda x: x.get("published", 0), reverse=True)
        
        # Build Bloomberg Terminal style markdown
        lines = ["## BLOOMBERG LATEST NEWS", "---"]
        
        for item in unique_items[:20]:
            # Parse Unix timestamp
            published = item.get("published", 0)
            time_str = format_timestamp(published) if published else ""
            
            title = item.get("title", item.get("headline", ""))
            url = item.get("url", item.get("shortURL", ""))
            cat = item.get("primarySite", "NEWS").upper()
            
            # Format: TIME | CATEGORY | [HEADLINE](URL)
            lines.append(f"**{time_str}** | `{cat}` | [{title}]({url})")
            lines.append("")
        
        markdown_content = "\n".join(lines)
        
        return {
            "results": [{"markdown_content": markdown_content}],
            "provider": "bloomberg",
            "warnings": None,
            "chart": None,
            "extra": {"metadata": {"route": "/news/markdown", "count": len(unique_items)}}
        }

@app.get("/news/iframe")
async def get_news_iframe():
    """Returns markdown with iframe to full terminal"""
    iframe_html = """
## BLOOMBERG TERMINAL

<iframe src="https://159.223.99.81/bloomberg/terminal" width="100%" height="600" frameborder="0"></iframe>

*Click headlines to open full articles*
"""
    return {
        "results": [{"markdown_content": iframe_html}],
        "provider": "bloomberg",
        "warnings": None,
        "chart": None,
        "extra": {"metadata": {"route": "/news/iframe"}}
    }

@app.get("/article")
async def get_full_article(url: str = Query(..., description="Bloomberg article URL")):
    """Fetch full article content via Apify Bloomberg scraper"""
    if not APIFY_API_TOKEN:
        raise HTTPException(status_code=500, detail="Apify API token not configured")
    
    if not url.startswith("https://www.bloomberg.com"):
        raise HTTPException(status_code=400, detail="Only Bloomberg URLs are supported")
    
    async with httpx.AsyncClient() as client:
        # Call Apify Bloomberg scraper synchronously
        apify_url = f"https://api.apify.com/v2/acts/romy~bloomberg-news-scraper/run-sync-get-dataset-items?token={APIFY_API_TOKEN}"
        
        try:
            response = await client.post(
                apify_url,
                json={"url": url},
                timeout=120.0  # Apify can take time to scrape
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Apify error: {response.text}")
            
            data = response.json()
            
            if data and len(data) > 0:
                article = data[0]
                return {
                    "success": True,
                    "article": {
                        "title": article.get("title", ""),
                        "subtitle": article.get("subtitle", ""),
                        "author": article.get("author", ""),
                        "date": article.get("date", ""),
                        "content": article.get("content", ""),
                        "images": article.get("images", []),
                        "url": url
                    }
                }
            else:
                return {"success": False, "error": "No content returned"}
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request timed out - article may be too long")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/terminal", response_class=HTMLResponse)
async def bloomberg_terminal():
    """Full Bloomberg Terminal HTML page with article modal"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Bloomberg Terminal</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000;
            color: #ff9900;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            padding: 10px;
        }
        .header {
            background: #1a1a2e;
            padding: 10px;
            border-bottom: 2px solid #ff9900;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #ff9900;
            font-size: 18px;
            font-weight: bold;
        }
        .tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 10px;
        }
        .tab {
            background: #1a1a2e;
            color: #ff9900;
            border: 1px solid #ff9900;
            padding: 5px 15px;
            cursor: pointer;
            font-family: inherit;
            font-size: 12px;
        }
        .tab:hover, .tab.active {
            background: #ff9900;
            color: #000;
        }
        .news-container {
            height: calc(100vh - 120px);
            overflow-y: auto;
        }
        .news-item {
            padding: 8px;
            border-bottom: 1px solid #333;
            cursor: pointer;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .news-item:hover {
            background: #1a1a2e;
        }
        .time {
            color: #00ff00;
            min-width: 50px;
        }
        .category {
            color: #00ffff;
            min-width: 100px;
            text-transform: uppercase;
        }
        .headline {
            color: #ff9900;
            flex: 1;
        }
        .read-btn {
            background: #ff9900;
            color: #000;
            border: none;
            padding: 4px 10px;
            cursor: pointer;
            font-size: 11px;
            font-weight: bold;
        }
        .read-btn:hover {
            background: #ffcc00;
        }
        .loading {
            color: #00ff00;
            padding: 20px;
            text-align: center;
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            overflow-y: auto;
        }
        .modal.active {
            display: block;
        }
        .modal-content {
            background: #1a1a2e;
            max-width: 900px;
            margin: 20px auto;
            padding: 30px;
            border: 2px solid #ff9900;
            color: #e0e0e0;
            font-family: Georgia, serif;
            font-size: 16px;
            line-height: 1.8;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #ff9900;
        }
        .modal-title {
            color: #ff9900;
            font-size: 28px;
            font-weight: bold;
            font-family: Georgia, serif;
            line-height: 1.3;
            flex: 1;
        }
        .modal-subtitle {
            color: #aaa;
            font-size: 18px;
            margin-top: 10px;
            font-style: italic;
        }
        .modal-meta {
            color: #00ffff;
            font-size: 14px;
            margin-bottom: 20px;
            font-family: 'Courier New', monospace;
        }
        .modal-buttons {
            display: flex;
            gap: 10px;
        }
        .modal-btn {
            background: #ff9900;
            color: #000;
            border: none;
            padding: 8px 16px;
            cursor: pointer;
            font-weight: bold;
            font-size: 12px;
        }
        .modal-btn:hover {
            background: #ffcc00;
        }
        .modal-btn.close {
            background: #666;
            color: #fff;
        }
        .modal-btn.close:hover {
            background: #888;
        }
        .article-content {
            color: #e0e0e0;
        }
        .article-content p {
            margin-bottom: 18px;
        }
        .article-content img {
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border: 1px solid #333;
        }
        .article-image {
            text-align: center;
            margin: 25px 0;
        }
        .article-image img {
            max-width: 100%;
            border: 1px solid #ff9900;
        }
        .article-image .caption {
            color: #888;
            font-size: 13px;
            margin-top: 8px;
            font-style: italic;
        }
        .loading-article {
            text-align: center;
            padding: 60px;
            color: #00ff00;
            font-size: 18px;
        }
        .loading-article .spinner {
            border: 4px solid #333;
            border-top: 4px solid #ff9900;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error-msg {
            color: #ff4444;
            text-align: center;
            padding: 40px;
        }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1a1a2e; }
        ::-webkit-scrollbar-thumb { background: #ff9900; }
        
        @media print {
            .modal-buttons { display: none; }
            .modal { background: white; }
            .modal-content { border: none; background: white; color: black; }
            .modal-title { color: black; }
            .article-content { color: black; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>BLOOMBERG TERMINAL - NEWS</h1>
        <span style="color: #00ff00; font-size: 11px;">Click READ to view full article (bypasses paywall)</span>
    </div>
    <div class="tabs">
        <button class="tab active" onclick="loadNews('all')">ALL</button>
        <button class="tab" onclick="loadNews('markets')">MARKETS</button>
        <button class="tab" onclick="loadNews('technology')">TECHNOLOGY</button>
        <button class="tab" onclick="loadNews('politics')">POLITICS</button>
        <button class="tab" onclick="loadNews('industries')">INDUSTRIES</button>
        <button class="tab" onclick="loadNews('wealth')">WEALTH</button>
    </div>
    <div class="news-container" id="news">
        <div class="loading">Loading...</div>
    </div>
    
    <!-- Article Modal -->
    <div class="modal" id="articleModal">
        <div class="modal-content" id="modalContent">
            <div class="loading-article">
                <div class="spinner"></div>
                <p>Loading full article...</p>
                <p style="font-size: 12px; color: #888;">This may take 30-60 seconds</p>
            </div>
        </div>
    </div>
    
    <script>
        let currentCategory = 'all';
        
        async function loadNews(category) {
            currentCategory = category;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('news').innerHTML = '<div class="loading">Loading ' + category.toUpperCase() + ' news...</div>';
            
            try {
                const response = await fetch('/bloomberg/stories/list?id=' + category);
                const data = await response.json();
                
                if (data.results) {
                    let html = '';
                    data.results.forEach(item => {
                        const encodedUrl = encodeURIComponent(item.url);
                        html += `
                            <div class="news-item">
                                <span class="time">${item.time}</span>
                                <span class="category">${item.category}</span>
                                <span class="headline">${item.headline}</span>
                                <button class="read-btn" onclick="openArticle('${encodedUrl}', event)">READ</button>
                            </div>
                        `;
                    });
                    document.getElementById('news').innerHTML = html;
                }
            } catch (err) {
                document.getElementById('news').innerHTML = '<div class="loading">Error loading news</div>';
            }
        }
        
        async function openArticle(encodedUrl, event) {
            event.stopPropagation();
            const url = decodeURIComponent(encodedUrl);
            const modal = document.getElementById('articleModal');
            const content = document.getElementById('modalContent');
            
            modal.classList.add('active');
            content.innerHTML = `
                <div class="loading-article">
                    <div class="spinner"></div>
                    <p>Loading full article...</p>
                    <p style="font-size: 12px; color: #888;">This may take 30-60 seconds (bypassing paywall)</p>
                </div>
            `;
            
            try {
                const response = await fetch('/bloomberg/article?url=' + encodedUrl);
                const data = await response.json();
                
                if (data.success && data.article) {
                    const article = data.article;
                    let imagesHtml = '';
                    
                    if (article.images && article.images.length > 0) {
                        article.images.forEach(img => {
                            imagesHtml += `
                                <div class="article-image">
                                    <img src="${img.url || img}" alt="${img.caption || 'Article image'}" />
                                    ${img.caption ? `<div class="caption">${img.caption}</div>` : ''}
                                </div>
                            `;
                        });
                    }
                    
                    content.innerHTML = `
                        <div class="modal-header">
                            <div>
                                <div class="modal-title">${article.title}</div>
                                ${article.subtitle ? `<div class="modal-subtitle">${article.subtitle}</div>` : ''}
                            </div>
                            <div class="modal-buttons">
                                <button class="modal-btn" onclick="savePDF()">SAVE PDF</button>
                                <button class="modal-btn" onclick="window.open('${url}', '_blank')">ORIGINAL</button>
                                <button class="modal-btn close" onclick="closeModal()">CLOSE</button>
                            </div>
                        </div>
                        <div class="modal-meta">
                            ${article.author ? `By ${article.author}` : ''} 
                            ${article.date ? ` | ${article.date}` : ''}
                        </div>
                        ${imagesHtml}
                        <div class="article-content" id="articleBody">
                            ${formatContent(article.content)}
                        </div>
                    `;
                } else {
                    content.innerHTML = `
                        <div class="error-msg">
                            <h2>Could not load article</h2>
                            <p>${data.error || 'Unknown error'}</p>
                            <br>
                            <button class="modal-btn" onclick="window.open('${url}', '_blank')">Open Original</button>
                            <button class="modal-btn close" onclick="closeModal()">Close</button>
                        </div>
                    `;
                }
            } catch (err) {
                content.innerHTML = `
                    <div class="error-msg">
                        <h2>Error loading article</h2>
                        <p>${err.message}</p>
                        <br>
                        <button class="modal-btn" onclick="window.open('${url}', '_blank')">Open Original</button>
                        <button class="modal-btn close" onclick="closeModal()">Close</button>
                    </div>
                `;
            }
        }
        
        function formatContent(content) {
            if (!content) return '<p>No content available</p>';
            // Split by double newlines to create paragraphs
            const paragraphs = content.split(/\\n\\n|\\r\\n\\r\\n/);
            return paragraphs.map(p => `<p>${p.trim()}</p>`).join('');
        }
        
        function closeModal() {
            document.getElementById('articleModal').classList.remove('active');
        }
        
        function savePDF() {
            const element = document.getElementById('modalContent');
            const title = element.querySelector('.modal-title')?.textContent || 'Bloomberg Article';
            
            const opt = {
                margin: 10,
                filename: title.substring(0, 50).replace(/[^a-z0-9]/gi, '_') + '.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            
            // Hide buttons temporarily
            const buttons = element.querySelector('.modal-buttons');
            if (buttons) buttons.style.display = 'none';
            
            html2pdf().set(opt).from(element).save().then(() => {
                if (buttons) buttons.style.display = 'flex';
            });
        }
        
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
        
        // Close modal on background click
        document.getElementById('articleModal').addEventListener('click', (e) => {
            if (e.target.id === 'articleModal') closeModal();
        });
        
        // Auto-refresh every 60 seconds
        setInterval(() => loadNews(currentCategory), 60000);
        
        // Initial load
        loadNews('all');
    </script>
</body>
</html>
"""
    return html

@app.get("/media/audios-trending")
async def get_trending_audios():
    """Get trending audio content"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/media/audios-trending",
            headers=headers,
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6901)
