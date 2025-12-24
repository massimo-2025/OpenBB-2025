from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Widget configuration for OpenBB Workspace
WIDGETS_CONFIG = {
    "bloomberg_news_markets": {
        "name": "Bloomberg Markets News",
        "description": "Latest market news from Bloomberg - Click headline to open article",
        "category": "News",
        "type": "table",
        "searchCategory": "News",
        "endpoint": "stories/list",
        "widgetId": "bloomberg_news_markets",
        "params": [
            {
                "paramName": "id",
                "label": "Category",
                "type": "form",
                "value": "markets",
                "description": "markets, technology, politics, industries, wealth, pursuits, businessweek, opinion"
            }
        ],
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {"field": "time", "headerName": "Time", "cellDataType": "text", "width": 80},
                    {"field": "headline", "headerName": "Headline", "cellDataType": "text", "flex": 1, "cellRenderer": "linkRenderer"},
                    {"field": "category", "headerName": "Category", "cellDataType": "text", "width": 100}
                ]
            }
        },
        "source": ["Bloomberg"]
    },
    "bloomberg_news_tech": {
        "name": "Bloomberg Technology News",
        "description": "Latest technology news from Bloomberg",
        "category": "News",
        "type": "table",
        "searchCategory": "News",
        "endpoint": "stories/list",
        "widgetId": "bloomberg_news_tech",
        "params": [
            {
                "paramName": "id",
                "label": "Category",
                "type": "form",
                "value": "technology",
                "description": "Category"
            }
        ],
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {"field": "time", "headerName": "Time", "cellDataType": "text", "width": 80},
                    {"field": "headline", "headerName": "Headline", "cellDataType": "text", "flex": 1, "cellRenderer": "linkRenderer"},
                    {"field": "category", "headerName": "Category", "cellDataType": "text", "width": 100}
                ]
            }
        },
        "source": ["Bloomberg"]
    },
    "bloomberg_news_politics": {
        "name": "Bloomberg Politics News",
        "description": "Latest political news from Bloomberg",
        "category": "News",
        "type": "table",
        "searchCategory": "News",
        "endpoint": "stories/list",
        "widgetId": "bloomberg_news_politics",
        "params": [
            {
                "paramName": "id",
                "label": "Category",
                "type": "form",
                "value": "politics",
                "description": "Category"
            }
        ],
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {"field": "time", "headerName": "Time", "cellDataType": "text", "width": 80},
                    {"field": "headline", "headerName": "Headline", "cellDataType": "text", "flex": 1, "cellRenderer": "linkRenderer"},
                    {"field": "category", "headerName": "Category", "cellDataType": "text", "width": 100}
                ]
            }
        },
        "source": ["Bloomberg"]
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
