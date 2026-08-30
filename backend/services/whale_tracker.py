import httpx
import asyncio
from typing import List, Dict, Any, Optional
from backend.config import WHALE_MIN_USD_VALUE, WHALE_VOLUME_MULTIPLIER

BINANCE_BASE_URL = "https://data-api.binance.vision/api/v3"

from backend.services.market_data import get_http_client

async def get_recent_large_trades(symbol: str, min_usd: float = WHALE_MIN_USD_VALUE, limit: int = 500) -> Dict[str, Any]:
    """
    Scan recent trades to identify Whale / Smart Money transactions.
    """
    clean_symbol = symbol.upper().replace("/", "").replace("-", "")
    url = f"{BINANCE_BASE_URL}/trades"
    params = {"symbol": clean_symbol, "limit": limit}
    
    client = get_http_client()
    try:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            trades = resp.json()
            whale_buys = []
            whale_sells = []
            total_whale_buy_usd = 0.0
            total_whale_sell_usd = 0.0
            
            for t in trades:
                price = float(t["price"])
                qty = float(t["qty"])
                usd_val = price * qty
                is_buyer_maker = t["isBuyerMaker"] # True means sell market order hit bid, False means buy market order hit ask
                
                if usd_val >= min_usd:
                    item = {
                        "id": t["id"],
                        "price": price,
                        "qty": qty,
                        "usd_value": round(usd_val, 2),
                        "side": "SELL" if is_buyer_maker else "BUY",
                        "time": t["time"]
                    }
                    if is_buyer_maker:
                        whale_sells.append(item)
                        total_whale_sell_usd += usd_val
                    else:
                        whale_buys.append(item)
                        total_whale_buy_usd += usd_val
                        
            total_whale_vol = total_whale_buy_usd + total_whale_sell_usd
            buy_pressure = (total_whale_buy_usd / (total_whale_vol + 1e-10)) * 100
            
            # Flow classification
            flow_status = "NET ACCUMULATION (BULLISH)" if buy_pressure >= 60 else \
                          "NET DISTRIBUTION (BEARISH)" if buy_pressure <= 40 else "BALANCED FLOW"
                          
            return {
                "symbol": symbol,
                "whale_trade_count": len(whale_buys) + len(whale_sells),
                "whale_buys_count": len(whale_buys),
                "whale_sells_count": len(whale_sells),
                "total_whale_buy_usd": round(total_whale_buy_usd, 2),
                "total_whale_sell_usd": round(total_whale_sell_usd, 2),
                "whale_buy_ratio": round(buy_pressure, 1),
                "flow_status": flow_status,
                "recent_whale_trades": sorted(whale_buys + whale_sells, key=lambda x: x["time"], reverse=True)[:15]
            }
        return {"error": "Failed to fetch trades"}
    except Exception as e:
        return {"error": str(e)}

async def scan_market_whale_activity(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Scan multiple symbols in parallel to find which coins have active whale inflow.
    """
    tasks = [get_recent_large_trades(s) for s in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    active_whales = []
    for s, res in zip(symbols, results):
        if isinstance(res, dict) and "whale_trade_count" in res:
            if res["whale_trade_count"] > 0:
                active_whales.append(res)
                
    # Sort by total whale buy activity
    active_whales.sort(key=lambda x: x.get("total_whale_buy_usd", 0), reverse=True)
    return active_whales
