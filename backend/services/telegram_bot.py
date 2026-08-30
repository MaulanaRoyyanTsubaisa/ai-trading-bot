import httpx
import asyncio
from typing import Dict, Any, Optional
from backend.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def format_signal_message(signal_data: Dict[str, Any]) -> str:
    """
    Format signal data into a professional telegram broadcast message.
    """
    symbol = signal_data["symbol"]
    signal = signal_data["signal"]
    action = signal_data["action"]
    confidence = signal_data["confidence"]
    curr_price = signal_data["current_price"]
    entry_zone = signal_data["entry_zone"]
    tp1 = signal_data["take_profit_1"]
    tp2 = signal_data["take_profit_2"]
    tp3 = signal_data["take_profit_3"]
    sl = signal_data["stop_loss"]
    rrr = signal_data["risk_reward_ratio"]
    timeframe = signal_data.get("timeframe", "1h")
    
    badge = "🟢🚀 [STRONG BUY]" if signal == "STRONG BUY" else \
            "🟢 [BUY / LONG]" if signal == "BUY" else \
            "🔴💥 [STRONG SELL]" if signal == "STRONG SELL" else \
            "🔴 [SELL / SHORT]" if signal == "SELL" else "⚪ [NEUTRAL / WAIT]"
            
    catalysts_text = "\n".join([f"  • {c}" for c in signal_data.get("catalysts", [])[:4]])
    
    msg = f"""
🤖 <b>AI SIGNAL TERMINAL ALERT</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>Asset:</b> #{symbol} ({timeframe})
⚡ <b>Sinyal:</b> {badge}
🔥 <b>Confidence:</b> <code>{confidence}%</code>
💲 <b>Current Price:</b> <code>${curr_price}</code>

📍 <b>Entry Zone:</b> <code>{entry_zone}</code>
🎯 <b>Target TP 1:</b> <code>${tp1}</code>
🎯 <b>Target TP 2:</b> <code>${tp2}</code>
🎯 <b>Target TP 3:</b> <code>${tp3}</code>
🛑 <b>Stop Loss:</b> <code>${sl}</code>
⚖️ <b>Risk/Reward:</b> <code>{rrr}</code>

📊 <b>Katalis Indikator:</b>
{catalysts_text if catalysts_text else "  • Multi-factor Technical Confluence"}

🐋 <b>Whale Flow:</b> {signal_data.get('whale_summary', {}).get('flow_status', 'Balanced')}

🧠 <b>AI Analyst Note:</b>
<i>{signal_data.get('ai_rationale', '')}</i>
━━━━━━━━━━━━━━━━━━━━
⚠️ <i>Disclaimer: Analisa berbasis AI & kuantitatif. Selalu gunakan risk management yang bijak.</i>
"""
    return msg.strip()

async def send_telegram_message(message: str, chat_id: Optional[str] = None) -> bool:
    """
    Send formatted HTML message to Telegram.
    """
    target_chat = chat_id or TELEGRAM_CHAT_ID
    if not TELEGRAM_BOT_TOKEN or not target_chat:
        print("[Telegram Bot] Bot Token or Chat ID not configured. Skipping live send.")
        return False
        
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                print(f"[Telegram Bot] Message sent successfully to {target_chat}")
                return True
            else:
                print(f"[Telegram Bot] Error sending message: {resp.text}")
                return False
        except Exception as e:
            print(f"[Telegram Bot] Exception: {e}")
            return False

async def send_signal_alert(signal_data: Dict[str, Any]) -> bool:
    message = format_signal_message(signal_data)
    return await send_telegram_message(message)

async def test_telegram_connection() -> Dict[str, Any]:
    """
    Check if bot token and chat are valid.
    """
    if not TELEGRAM_BOT_TOKEN:
        return {"status": "error", "message": "TELEGRAM_BOT_TOKEN belum diisi di .env"}
        
    url = f"{TELEGRAM_API_URL}/getMe"
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                bot_info = resp.json().get("result", {})
                return {
                    "status": "success",
                    "bot_name": bot_info.get("first_name"),
                    "bot_username": bot_info.get("username"),
                    "chat_id_configured": bool(TELEGRAM_CHAT_ID)
                }
            return {"status": "error", "message": f"Telegram API Error: {resp.text}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
