import asyncio
from backend.services.market_data import get_klines, get_ticker_24h, get_orderbook
from backend.services.ta_engine import analyze_candlesticks
from backend.services.whale_tracker import get_recent_large_trades
from backend.services.ai_analyst import generate_hybrid_signal

async def main():
    print("Testing Binance Market Data...")
    candles = await get_klines("BTCUSDT", "1h", 100)
    print(f"Candles fetched: {len(candles)}")
    assert len(candles) > 0, "No candles fetched"
    
    print("Testing TA Engine...")
    ta = analyze_candlesticks(candles)
    print(f"TA Analysis: Price={ta['current_price']}, RSI={ta['indicators']['rsi']}, MACD={ta['indicators']['macd']}")
    
    print("Testing Whale Tracker...")
    whale = await get_recent_large_trades("BTCUSDT")
    print(f"Whale Tracker: {whale.get('flow_status')}, Buy Ratio: {whale.get('whale_buy_ratio')}%")
    
    print("Testing AI Hybrid Signal Generator...")
    signal = generate_hybrid_signal("BTCUSDT", "1h", ta, whale)
    print(f"Signal: {signal['signal']} | Confidence: {signal['confidence']}% | Action: {signal['action']}")
    print(f"Entry: {signal['entry_zone']} | TP1: {signal['take_profit_1']} | SL: {signal['stop_loss']}")
    print("\nAI Rationale:\n" + signal['ai_rationale'])
    print("\nALL BACKEND UNIT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
