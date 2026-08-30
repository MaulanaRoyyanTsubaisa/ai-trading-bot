import httpx
import asyncio

BOT_TOKEN = "8619951287:AAFupHkTgEHsj-Yy1e1-HFahisLXGtlxMUg"

async def test_ids():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Test 1: ID 8619951287 (Bot ID)
    async with httpx.AsyncClient() as client:
        r1 = await client.post(url, json={"chat_id": "8619951287", "text": "Test ID 1"})
        print("Test 8619951287:", r1.status_code, r1.json())
        
        # Test 2: ID 1077659740 (User ID)
        r2 = await client.post(url, json={"chat_id": "1077659740", "text": "Test ID 2 (Akun Pribadi Anda)"})
        print("Test 1077659740:", r2.status_code, r2.json())

if __name__ == "__main__":
    asyncio.run(test_ids())
