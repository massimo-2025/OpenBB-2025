from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os

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

WIDGETS_CONFIG = {
    "bloomberg_news_markets": {
        "name": "Bloomberg Markets News",
        "description": "Latest market news from Bloomberg",
        "category": "News",
        "type": "table",
        "searchCategory": "News",
        "endpoint": "stories/list",
        "widgetId": "bloomberg_news_markets",
        "params": [
            {
                "name": "id",
                "label": "Category",
                "type": "text",
                "default": "markets",
                "description": "News category: markets, technology, politics, industries"
            }
        ],
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {"field": "title", "headerName": "Title", "cellDataType": "text"},
                    {"field": "published", "headerName": "Published", "cellDataType": "number"},
                    {"field": "primarySite", "headerName": "Category", "cellDataType": "text"},
                    {"field": "shortURL", "headerName": "URL", "cellDataType": "text"}
                ]
            }
        },
        "source": ["Bloomberg via RapidAPI"]
    },
    "bloomberg_news_region": {
        "name": "Bloomberg Regional News",
        "description": "News by region from Bloomberg",
        "category": "News",
        "type": "table",
        "searchCategory": "News",
        "endpoint": "news/list-by-region",
        "widgetId": "bloomberg_news_region",
        "params": [
            {
                "name": "id",
                "label": "Region",
                "type": "text",
                "default": "us",
                "description": "Region: us, europe, asia"
            }
        ],
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {"field": "title", "headerName": "Title", "cellDataType": "text"},
                    {"field": "published", "headerName": "Published", "cellDataType": "number"},
                    {"field": "shortURL", "headerName": "URL", "cellDataType": "text"}
                ]
            }
        },
        "source": ["Bloomberg via RapidAPI"]
    },
    "bloomberg_market_movers": {
        "name": "Bloomberg Market Movers",
        "description": "Top market movers from Bloomberg",
        "category": "Markets",
        "type": "table",
        "searchCategory": "Markets",
        "endpoint": "market/get-movers",
        "widgetId": "bloomberg_market_movers",
        "params": [
            {
                "name": "id",
                "label": "Market",
                "type": "text",
                "default": "us",
                "description": "Market: us, europe, asia"
            }
        ],
        "data": {
            "table": {
                "showAll": True
            }
        },
        "source": ["Bloomberg via RapidAPI"]
    }
}

@app.get("/widgets.json")
async def get_widgets():
    return JSONResponse(content=WIDGETS_CONFIG)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/stories/list")
async def get_stories_list(id: str = Query("markets", description="Category: markets, technology, politics, industries, etc.")):
    """Get stories/news by category"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/stories/list",
            headers=headers,
            params={"id": id},
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.get("/news/list-by-region")
async def get_news_by_region(id: str = Query("us", description="Region: us, europe, asia, etc.")):
    """Get news by region"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/news/list-by-region",
            headers=headers,
            params={"id": id},
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.get("/market/get-movers")
async def get_market_movers(id: str = Query("us", description="Market: us, europe, asia, etc.")):
    """Get market movers"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/market/get-movers",
            headers=headers,
            params={"id": id},
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

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
