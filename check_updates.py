import httpx
import asyncio

TELEGRAM_BOT_TOKEN = "8619951287:AAFupHkTgEHsj-Yy1e1-HFahisLXGtlxMUg"

async def check_updates():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        data = resp.json()
        print("getUpdates Result:", data)
        
        if data.get("ok") and data.get("result"):
            for update in data["result"]:
                msg = update.get("message") or update.get("channel_post") or update.get("my_chat_member", {}).get("chat")
                if msg:
                    chat = msg.get("chat", {})
                    print(f"Found Chat ID: {chat.get('id')} | Type: {chat.get('type')} | Username: {chat.get('username')} | Title/Name: {chat.get('first_name') or chat.get('title')}")

if __name__ == "__main__":
    asyncio.run(check_updates())
