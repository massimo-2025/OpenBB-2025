from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/news/trending")
async def get_trending_news():
    """Get trending news from Bloomberg"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/news/trending",
            headers=headers,
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.get("/news/stock")
async def get_stock_news(symbol: str = Query(..., description="Stock symbol e.g. AAPL")):
    """Get news for a specific stock"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/news/stock",
            headers=headers,
            params={"symbol": symbol},
            timeout=30.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@app.get("/news/list")
async def get_news_list(id: str = Query("markets", description="Category: markets, technology, politics, etc.")):
    """Get news by category"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{RAPIDAPI_HOST}/news/list",
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
