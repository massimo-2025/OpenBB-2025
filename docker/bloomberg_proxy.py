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
RAPIDAPI_HOST = "bloomberg-finance.p.rapidapi.com"

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
async def get_stories_list(id: str = Query("markets", description="Category: markets, technology, politics, industries")):
    """Get stories/news by category - formatted for Bloomberg Terminal style"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/stories/list",
            headers=headers,
            params={"id": id},
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        
        # Format response for OpenBB table with clickable links
        if data.get("status") and data.get("data"):
            formatted_results = []
            for item in data["data"]:
                formatted_results.append({
                    "time": format_timestamp(item.get("published", 0)),
                    "headline": item.get("title", ""),
                    "category": item.get("primarySite", "").upper(),
                    "url": item.get("shortURL", item.get("longURL", "")),
                    "thumbnail": item.get("thumbnailImage", "")
                })
            
            return {
                "results": formatted_results,
                "provider": "bloomberg",
                "warnings": None,
                "chart": None,
                "extra": {"metadata": {"route": "/stories/list", "category": id}}
            }
        
        return data

@app.get("/news/markdown")
async def get_news_markdown(category: str = Query("markets", description="Category: markets, technology, politics")):
    """Get news formatted as markdown with clickable links - Bloomberg Terminal style"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/stories/list",
            headers=headers,
            params={"id": category},
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        data = response.json()
        
        if data.get("status") and data.get("data"):
            # Build Bloomberg Terminal style markdown
            lines = [f"## BLOOMBERG {category.upper()} NEWS", "---"]
            
            for item in data["data"][:20]:  # Limit to 20 items
                time_str = format_timestamp(item.get("published", 0))
                title = item.get("title", "")
                url = item.get("shortURL", item.get("longURL", ""))
                cat = item.get("primarySite", "").upper()
                
                # Format: TIME | CATEGORY | [HEADLINE](URL)
                lines.append(f"**{time_str}** | `{cat}` | [{title}]({url})")
                lines.append("")
            
            markdown_content = "\n".join(lines)
            
            return {
                "results": [{"markdown_content": markdown_content}],
                "provider": "bloomberg",
                "warnings": None,
                "chart": None,
                "extra": {"metadata": {"route": "/news/markdown", "category": category}}
            }
        
        return {"results": [], "provider": "bloomberg"}

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

@app.get("/terminal", response_class=HTMLResponse)
async def bloomberg_terminal():
    """Full Bloomberg Terminal HTML page"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Bloomberg Terminal</title>
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
        .headline a {
            color: #ff9900;
            text-decoration: none;
        }
        .headline a:hover {
            text-decoration: underline;
            color: #ffcc00;
        }
        .loading {
            color: #00ff00;
            padding: 20px;
            text-align: center;
        }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1a1a2e; }
        ::-webkit-scrollbar-thumb { background: #ff9900; }
    </style>
</head>
<body>
    <div class="header">
        <h1>BLOOMBERG TERMINAL - NEWS</h1>
    </div>
    <div class="tabs">
        <button class="tab active" onclick="loadNews('markets')">MARKETS</button>
        <button class="tab" onclick="loadNews('technology')">TECHNOLOGY</button>
        <button class="tab" onclick="loadNews('politics')">POLITICS</button>
        <button class="tab" onclick="loadNews('industries')">INDUSTRIES</button>
        <button class="tab" onclick="loadNews('wealth')">WEALTH</button>
    </div>
    <div class="news-container" id="news">
        <div class="loading">Loading...</div>
    </div>
    <script>
        let currentCategory = 'markets';
        
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
                        html += `
                            <div class="news-item" onclick="window.open('${item.url}', '_blank')">
                                <span class="time">${item.time}</span>
                                <span class="category">${item.category}</span>
                                <span class="headline"><a href="${item.url}" target="_blank">${item.headline}</a></span>
                            </div>
                        `;
                    });
                    document.getElementById('news').innerHTML = html;
                }
            } catch (err) {
                document.getElementById('news').innerHTML = '<div class="loading">Error loading news</div>';
            }
        }
        
        // Auto-refresh every 60 seconds
        setInterval(() => loadNews(currentCategory), 60000);
        
        // Initial load
        loadNews('markets');
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
