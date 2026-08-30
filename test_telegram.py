import httpx
import asyncio
from backend.services.telegram_bot import test_telegram_connection, send_signal_alert
from backend.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def main():
    print(f"Testing Telegram Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"Target Chat: {TELEGRAM_CHAT_ID}")
    
    # 1. Test getMe
    res = await test_telegram_connection()
    print("Bot Info:", res)
    
    # 2. Test sending signal
    sample_signal = {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "signal": "STRONG BUY",
        "action": "LONG",
        "confidence": 92,
        "current_price": 78650.0,
        "entry_zone": "$78400 - $78800",
        "take_profit_1": 79800.0,
        "take_profit_2": 81500.0,
        "take_profit_3": 84000.0,
        "stop_loss": 77200.0,
        "risk_reward_ratio": "1:2.9",
        "whale_summary": {"flow_status": "NET ACCUMULATION (BULLISH)"},
        "catalysts": ["RSI Oversold Rebound (32.4)", "MACD Golden Cross", "Whale Inflow +$8.5M"],
        "ai_rationale": "Setup konfirmasi pola reversal valid. Terdeteksi lonjakan volume akumulasi institusi di atas support 77.200 dengan target utama TP2 di 81.500."
    }
    
    sent = await send_signal_alert(sample_signal)
    print("Send Signal Result:", "SUCCESS" if sent else "FAILED")

if __name__ == "__main__":
    asyncio.run(main())
