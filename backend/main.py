import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any

from backend.config import DEFAULT_SYMBOLS, DEFAULT_TIMEFRAME, HOST, PORT
from backend.services.market_data import get_klines, get_ticker_24h, get_orderbook
from backend.services.ta_engine import analyze_candlesticks
from backend.services.whale_tracker import get_recent_large_trades, scan_market_whale_activity
from backend.services.ai_analyst import generate_hybrid_signal, generate_deep_ai_insights
from backend.services.telegram_bot import send_signal_alert, send_telegram_message, test_telegram_connection
from backend.services.scheduler import background_scanner_loop, run_full_market_scan, analyze_single_symbol, signal_history

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run initial market scan and launch background loop
    print("[STARTUP] AI Trading Signal Bot & Terminal starting up...")
    asyncio.create_task(run_full_market_scan())
    asyncio.create_task(background_scanner_loop())
    yield
    print("[SHUTDOWN] AI Trading Signal Bot shutting down...")

app = FastAPI(
    title="AI Trading Signal Terminal API",
    description="Professional AI Market Screener, Whale Tracker, & Signal Bot",
    version="1.0.0",
    lifespan=lifespan
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Enable CORS for Frontend Terminal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "online",
        "service": "AI Trading Signal Bot & Terminal",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/status")
async def get_system_status():
    tg_status = await test_telegram_connection()
    return {
        "status": "online",
        "monitored_symbols_count": len(DEFAULT_SYMBOLS),
        "active_signals_count": len(signal_history),
        "telegram_integration": tg_status,
        "default_timeframe": DEFAULT_TIMEFRAME
    }

@app.get("/api/market/ticker")
async def get_tickers(symbol: Optional[str] = None):
    data = await get_ticker_24h(symbol)
    return {"data": data}

@app.get("/api/market/klines")
async def get_candlesticks(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100):
    candles = await get_klines(symbol, interval=interval, limit=limit)
    if not candles:
        raise HTTPException(status_code=404, detail="Candlestick data not found")
    return {"symbol": symbol, "interval": interval, "candles": candles}

@app.get("/api/market/orderbook")
async def get_book(symbol: str = "BTCUSDT", limit: int = 50):
    book = await get_orderbook(symbol, limit=limit)
    return book

from backend.services.signal_tracker import get_performance_summary, update_tracked_signals

@app.get("/api/performance")
async def get_performance():
    summary = await update_tracked_signals()
    return summary

@app.get("/api/signals")
async def get_signals():
    # If history is empty, run quick scan
    if not signal_history:
        await run_full_market_scan(DEFAULT_SYMBOLS[:4])
    return {"signals": signal_history}

@app.get("/api/signals/analyze")
async def analyze_symbol(symbol: str = "BTCUSDT", timeframe: str = "1h"):
    sig = await analyze_single_symbol(symbol, timeframe)
    if not sig:
        raise HTTPException(status_code=400, detail=f"Gagal menganalisa simbol {symbol}")
    return sig

@app.post("/api/scan")
async def trigger_scan(symbols: Optional[List[str]] = Body(None), timeframe: str = Body("1h")):
    target_symbols = symbols or DEFAULT_SYMBOLS
    signals = await run_full_market_scan(target_symbols, timeframe)
    return {
        "status": "success",
        "scanned_count": len(signals),
        "signals": signals
    }

@app.get("/api/whale/activity")
async def get_whale_activity():
    activity = await scan_market_whale_activity(DEFAULT_SYMBOLS)
    return {"whales": activity}

@app.post("/api/copilot/chat")
async def ai_copilot_chat(payload: Dict[str, Any] = Body(...)):
    message = payload.get("message", "")
    symbol = payload.get("symbol", "BTCUSDT")
    timeframe = payload.get("timeframe", "1h")
    
    # Fetch real-time market data to ground AI reasoning
    candles = await get_klines(symbol, interval=timeframe, limit=100)
    ta_data = analyze_candlesticks(candles) if candles else {}
    whale_data = await get_recent_large_trades(symbol)
    
    # Try LLM if available
    llm_insight = await generate_deep_ai_insights({
        "question": message,
        "symbol": symbol,
        "timeframe": timeframe,
        "technical_data": ta_data,
        "whale_data": whale_data
    })
    
    if llm_insight:
        return {"reply": llm_insight}
        
    # Smart Fallback AI Response Engine
    if ta_data and "indicators" in ta_data:
        ind = ta_data["indicators"]
        curr_p = ta_data["current_price"]
        rsi = ind["rsi"]
        cmf = ind["cmf"]
        st = "BULLISH" if ind["supertrend_bullish"] else "BEARISH"
        
        reply = (
            f"📊 **Analisa Copilot AI untuk {symbol} ({timeframe})**:\n\n"
            f"• **Harga Saat Ini:** ${curr_p}\n"
            f"• **RSI (14):** {rsi} ({'Jenuh Jual (Oversold)' if rsi < 30 else 'Jenuh Beli (Overbought)' if rsi > 70 else 'Netral/Momentum'})\n"
            f"• **SuperTrend:** {st}\n"
            f"• **Whale Money Flow (CMF):** {cmf:.3f} ({'Akumulasi Masuk' if cmf > 0 else 'Distribusi Keluar'})\n\n"
            f"💡 **Rekomendasi AI:**\n"
            f"Kondisi teknikal menunjukkan struktur {st.lower()} dengan support kuat di ${ta_data['levels']['support_1']} "
            f"dan resistensi di ${ta_data['levels']['resistance_1']}. "
            f"{'Peluang buy on breakout/rebound terbuka.' if st == 'BULLISH' else 'Waspadai tekanan jual lanjutan, tunggu konfirmasi support.'}"
        )
        return {"reply": reply}
    else:
        return {"reply": f"Menganalisa pergerakan pasar untuk {symbol}. Silakan pantau zona support dan level volume sebelum entry."}

@app.post("/api/telegram/test")
async def send_test_telegram():
    live_signal = await analyze_single_symbol("BTCUSDT", "1h")
    if not live_signal:
        # Fallback to fetching live klines directly
        candles = await get_klines("BTCUSDT", "1h", 100)
        ta_result = analyze_candlesticks(candles)
        whale_result = await get_recent_large_trades("BTCUSDT")
        live_signal = generate_hybrid_signal("BTCUSDT", "1h", ta_result, whale_result)
        
    sent = await send_signal_alert(live_signal)
    return {
        "success": sent,
        "message": f"Pesan sinyal REAL-TIME {live_signal['symbol']} (Harga Aktual: ${live_signal['current_price']}) terkirim ke Telegram!" if sent else "Gagal mengirim ke Telegram.",
        "signal": live_signal
    }

@app.post("/api/telegram/dispatch")
async def dispatch_signal_to_telegram(signal: Dict[str, Any] = Body(...)):
    sent = await send_signal_alert(signal)
    return {"success": sent}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
