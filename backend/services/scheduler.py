import asyncio
import time
from typing import List, Dict, Any, Optional
from backend.config import DEFAULT_SYMBOLS, DEFAULT_TIMEFRAME, MIN_CONFIDENCE_ALERT, SCAN_INTERVAL_MINUTES
from backend.services.market_data import get_klines
from backend.services.ta_engine import analyze_candlesticks
from backend.services.whale_tracker import get_recent_large_trades
from backend.services.ai_analyst import generate_hybrid_signal
from backend.services.telegram_bot import send_signal_alert

from backend.services.signal_tracker import record_new_signal, update_tracked_signals

# In-memory storage for signals & scans
signal_history: List[Dict[str, Any]] = []
last_alerted_timestamps: Dict[str, float] = {}
is_scanner_running = False

async def analyze_single_symbol(symbol: str, timeframe: str = DEFAULT_TIMEFRAME) -> Optional[Dict[str, Any]]:
    try:
        candles = await get_klines(symbol, interval=timeframe, limit=100)
        if not candles or len(candles) < 30:
            return None
            
        ta_result = analyze_candlesticks(candles)
        if "error" in ta_result:
            return None
            
        whale_result = await get_recent_large_trades(symbol)
        signal = generate_hybrid_signal(symbol, timeframe, ta_result, whale_result)
        signal["timestamp"] = int(time.time())
        
        # If actionable signal with good confidence, register into performance checklist tracker
        if signal.get("action") in ["LONG", "SHORT"] and signal.get("confidence", 0) >= MIN_CONFIDENCE_ALERT:
            record_new_signal(signal)
            
        return signal
    except Exception as e:
        print(f"[Scanner] Error analyzing {symbol}: {e}")
        return None

async def run_full_market_scan(symbols: List[str] = DEFAULT_SYMBOLS, timeframe: str = DEFAULT_TIMEFRAME) -> List[Dict[str, Any]]:
    tasks = [analyze_single_symbol(s, timeframe) for s in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_signals = []
    for s, res in zip(symbols, results):
        if isinstance(res, dict) and "signal" in res:
            valid_signals.append(res)
            
    # Sort signals by confidence descending
    valid_signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    
    # Update global signal history (keep max 100)
    global signal_history
    for sig in valid_signals:
        # Avoid duplicate consecutive signals
        existing = [idx for idx, x in enumerate(signal_history) if x["symbol"] == sig["symbol"]]
        if existing:
            signal_history[existing[0]] = sig
        else:
            signal_history.insert(0, sig)
            
    signal_history = signal_history[:100]
    return valid_signals

async def background_scanner_loop():
    global is_scanner_running
    is_scanner_running = True
    print(f"[Scanner Loop] Starting background scanner every {SCAN_INTERVAL_MINUTES} minutes...")
    
    while is_scanner_running:
        try:
            print("[Scanner Loop] Running scheduled market scan & performance tracker...")
            signals = await run_full_market_scan()
            await update_tracked_signals()
            
            # Check for high confidence signals to send to Telegram
            current_time = time.time()
            for sig in signals:
                sym = sig["symbol"]
                conf = sig["confidence"]
                action = sig["action"]
                
                # Check alert criteria (High confidence + Non-neutral action)
                if conf >= MIN_CONFIDENCE_ALERT and action in ["LONG", "SHORT"]:
                    last_alert = last_alerted_timestamps.get(sym, 0)
                    # Alert cooldown: 30 minutes for the same symbol
                    if current_time - last_alert > 1800:
                        print(f"[Scanner Alert] Triggering alert for {sym} ({sig['signal']} - {conf}%)")
                        await send_signal_alert(sig)
                        last_alerted_timestamps[sym] = current_time
                        
        except Exception as e:
            print(f"[Scanner Loop] Error in scanner iteration: {e}")
            
        # Wait for the next interval
        await asyncio.sleep(SCAN_INTERVAL_MINUTES * 60)
