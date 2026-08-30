import httpx
import asyncio
from typing import List, Dict, Any, Optional

BINANCE_BASE_URLS = [
    "https://data-api.binance.vision/api/v3",
    "https://api.binance.com/api/v3",
    "https://api1.binance.com/api/v3",
    "https://api3.binance.com/api/v3"
]
BINANCE_BASE_URL = BINANCE_BASE_URLS[0]

_http_client: Optional[httpx.AsyncClient] = None

def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(6.0, connect=3.0),
            headers={"User-Agent": "Mozilla/5.0"}
        )
    return _http_client

async def get_klines(symbol: str, interval: str = "1h", limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch OHLCV candlestick data from Binance.
    interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 1w
    """
    clean_symbol = symbol.upper().replace("/", "").replace("-", "")
    url = f"{BINANCE_BASE_URL}/klines"
    params = {
        "symbol": clean_symbol,
        "interval": interval,
        "limit": limit
    }
    
    client = get_http_client()
    try:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            candles = []
            for row in data:
                candles.append({
                    "time": int(row[0]) // 1000, # Unix timestamp in seconds
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                    "close_time": int(row[6]) // 1000,
                    "quote_volume": float(row[7]),
                    "trades_count": int(row[8]),
                    "taker_buy_base": float(row[9]),
                    "taker_buy_quote": float(row[10])
                })
            return candles
        else:
            return []
    except Exception as e:
        return []

async def get_ticker_24h(symbol: Optional[str] = None) -> Any:
    """
    Fetch 24h price change statistics.
    """
    url = f"{BINANCE_BASE_URL}/ticker/24hr"
    params = {}
    if symbol:
        clean_symbol = symbol.upper().replace("/", "").replace("-", "")
        params["symbol"] = clean_symbol

    client = get_http_client()
    try:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return [
                    {
                        "symbol": item["symbol"],
                        "price": float(item["lastPrice"]),
                        "change_percent": float(item["priceChangePercent"]),
                        "high_24h": float(item["highPrice"]),
                        "low_24h": float(item["lowPrice"]),
                        "volume_24h": float(item["volume"]),
                        "quote_volume_24h": float(item["quoteVolume"]),
                    }
                    for item in data
                    if item["symbol"].endswith("USDT")
                ]
            else:
                return {
                    "symbol": data["symbol"],
                    "price": float(data["lastPrice"]),
                    "change_percent": float(data["priceChangePercent"]),
                    "high_24h": float(data["highPrice"]),
                    "low_24h": float(data["lowPrice"]),
                    "volume_24h": float(data["volume"]),
                    "quote_volume_24h": float(data["quoteVolume"]),
                }
        return [] if symbol is None else {}
    except Exception as e:
        return [] if symbol is None else {}

async def get_orderbook(symbol: str, limit: int = 50) -> Dict[str, Any]:
    """
    Fetch order book depth to evaluate bid/ask pressure.
    """
    clean_symbol = symbol.upper().replace("/", "").replace("-", "")
    url = f"{BINANCE_BASE_URL}/depth"
    params = {"symbol": clean_symbol, "limit": limit}

    client = get_http_client()
    try:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            bids = [{"price": float(b[0]), "qty": float(b[1])} for b in data.get("bids", [])]
            asks = [{"price": float(a[0]), "qty": float(a[1])} for a in data.get("asks", [])]
            total_bid_volume = sum(b["price"] * b["qty"] for b in bids)
            total_ask_volume = sum(a["price"] * a["qty"] for a in asks)
            
            bid_ask_ratio = total_bid_volume / (total_ask_volume + 1e-6)
            
            return {
                "symbol": symbol,
                "bids": bids,
                "asks": asks,
                "total_bid_usd": round(total_bid_volume, 2),
                "total_ask_usd": round(total_ask_volume, 2),
                "bid_ask_ratio": round(bid_ask_ratio, 2),
                "buyer_dominance": round((total_bid_volume / (total_bid_volume + total_ask_volume + 1e-6)) * 100, 1)
            }
        return {"error": "Failed to fetch order book"}
    except Exception as e:
        return {"error": str(e)}
