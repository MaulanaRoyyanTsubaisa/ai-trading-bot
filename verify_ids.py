import httpx
import asyncio
from backend.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def test_ids():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID belum dikonfigurasi di .env")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": "✅ Tes koneksi AI Trading Bot"},
        )
        print("Telegram test:", response.status_code, response.json().get("ok", False))

if __name__ == "__main__":
    asyncio.run(test_ids())
