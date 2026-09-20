import httpx
from html import escape
from typing import Dict, Any, Optional
from backend.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def _display_price(symbol: str, value: Any) -> str:
    """Keep legacy display unchanged except for PEPE's sub-cent prices."""
    if str(symbol).upper() == "PEPEUSDT":
        return f"{float(value):.8f}"
    return str(value)

def format_signal_message(
    signal_data: Dict[str, Any], checklist: Optional[Dict[str, bool]] = None,
    status: str = "IN_PROGRESS"
) -> str:
    """
    Format signal data into a professional telegram broadcast message.
    """
    symbol = signal_data["symbol"]
    signal = signal_data["signal"]
    action = signal_data["action"]
    confidence = signal_data["confidence"]
    curr_price = _display_price(symbol, signal_data["current_price"])
    entry_zone = signal_data["entry_zone"]
    tp1 = _display_price(symbol, signal_data["take_profit_1"])
    tp2 = _display_price(symbol, signal_data["take_profit_2"])
    tp3 = _display_price(symbol, signal_data["take_profit_3"])
    sl = _display_price(symbol, signal_data["stop_loss"])
    rrr = signal_data["risk_reward_ratio"]
    timeframe = signal_data.get("timeframe", "1h")
    
    badge = "🟢🚀 [STRONG BUY]" if signal == "STRONG BUY" else \
            "🟢 [BUY / LONG]" if signal == "BUY" else \
            "🔴💥 [STRONG SELL]" if signal == "STRONG SELL" else \
            "🔴 [SELL / SHORT]" if signal == "SELL" else "⚪ [NEUTRAL / WAIT]"
            
    checklist = checklist or {}
    mark = lambda key: "✅" if checklist.get(key, False) else "⬜"
    catalysts_text = "\n".join(
        [f"  • {escape(str(c))}" for c in signal_data.get("catalysts", [])[:4]]
    )
    
    msg = f"""
🤖 <b>AI SIGNAL TERMINAL ALERT</b>
━━━━━━━━━━━━━━━━━━━━
🎯 <b>Asset:</b> #{symbol} ({timeframe})
⚡ <b>Sinyal:</b> {badge}
🔥 <b>Confidence:</b> <code>{confidence}%</code>
💲 <b>Current Price:</b> <code>${curr_price}</code>

📍 <b>Entry Zone:</b> <code>{entry_zone}</code>
{mark('tp1_reached')} <b>Target TP 1:</b> <code>${tp1}</code>
{mark('tp2_reached')} <b>Target TP 2:</b> <code>${tp2}</code>
{mark('tp3_reached')} <b>Target TP 3:</b> <code>${tp3}</code>
{mark('sl_triggered')} <b>Stop Loss:</b> <code>${sl}</code>
⚖️ <b>Risk/Reward:</b> <code>{rrr}</code>

📊 <b>Katalis Indikator:</b>
{catalysts_text if catalysts_text else "  • Multi-factor Technical Confluence"}

🐋 <b>Whale Flow:</b> {signal_data.get('whale_summary', {}).get('flow_status', 'Balanced')}

🧠 <b>AI Analyst Note:</b>
<i>{escape(str(signal_data.get('ai_rationale', '')))}</i>
📌 <b>Status:</b> {escape(status)}
━━━━━━━━━━━━━━━━━━━━
⚠️ <i>Disclaimer: Analisa berbasis AI & kuantitatif. Selalu gunakan risk management yang bijak.</i>
"""
    return msg.strip()

async def send_telegram_message(
    message: str,
    chat_id: Optional[str] = None,
    reply_to_message_id: Optional[int] = None,
) -> Optional[int]:
    """
    Send formatted HTML message to Telegram.
    """
    target_chat = chat_id or TELEGRAM_CHAT_ID
    if not TELEGRAM_BOT_TOKEN or not target_chat:
        print("[Telegram Bot] Bot Token or Chat ID not configured. Skipping live send.")
        return None
        
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_to_message_id is not None:
        payload["reply_parameters"] = {
            "message_id": int(reply_to_message_id),
            "allow_sending_without_reply": True,
        }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                print(f"[Telegram Bot] Message sent successfully to {target_chat}")
                return resp.json().get("result", {}).get("message_id")
            else:
                print(f"[Telegram Bot] Error sending message: {resp.text}")
                return None
        except Exception as e:
            print(f"[Telegram Bot] Exception: {e}")
            return None

async def edit_telegram_message(
    message_id: int, message: str, chat_id: Optional[str] = None
) -> bool:
    target_chat = chat_id or TELEGRAM_CHAT_ID
    if not TELEGRAM_BOT_TOKEN or not target_chat:
        return False
    payload = {
        "chat_id": target_chat,
        "message_id": int(message_id),
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(f"{TELEGRAM_API_URL}/editMessageText", json=payload)
            if resp.status_code == 200:
                return True
            # Telegram returns this harmless error if content is already identical.
            if resp.status_code == 400 and "message is not modified" in resp.text.lower():
                return True
            print(f"[Telegram Bot] Error editing message: {resp.text}")
            return False
        except Exception as exc:
            print(f"[Telegram Bot] Edit exception: {exc}")
            return False

def format_progress_message(item: Dict[str, Any], level: str, price: float) -> str:
    checklist = item["checklist"]
    mark = lambda key: "✅" if checklist.get(key, False) else "⬜"
    icon = "🛑" if level == "SL" else "✅"
    return (
        f"{icon} <b>{escape(level)} HIT — {escape(item['symbol'])} {escape(item['action'])}</b>\n"
        f"Harga terpantau: <code>${_display_price(item['symbol'], price)}</code>\n"
        f"Progress: {mark('tp1_reached')} TP1  {mark('tp2_reached')} TP2  "
        f"{mark('tp3_reached')} TP3  {mark('sl_triggered')} SL\n"
        f"Status: <b>{escape(item['status'])}</b>\n"
        "↩️ Update ini me-reply sinyal awal agar progres mudah dilacak."
    )

async def send_signal_alert(
    signal_data: Dict[str, Any], checklist: Optional[Dict[str, bool]] = None,
    status: str = "IN_PROGRESS"
) -> Optional[int]:
    message = format_signal_message(signal_data, checklist, status)
    return await send_telegram_message(message)

async def send_progress_alert(item: Dict[str, Any], level: str, price: float) -> Optional[int]:
    message_id = item.get("telegram_message_id")
    if not message_id:
        return None
    return await send_telegram_message(
        format_progress_message(item, level, price),
        reply_to_message_id=message_id,
    )

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
