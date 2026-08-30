import asyncio
import httpx

ENDPOINTS = [
    "https://api.binance.com/api/v3/ping",
    "https://data-api.binance.vision/api/v3/ping",
    "https://api1.binance.com/api/v3/ping",
    "https://api2.binance.com/api/v3/ping",
    "https://api3.binance.com/api/v3/ping",
    "https://api4.binance.com/api/v3/ping",
    "https://api.coingecko.com/api/v3/ping"
]

async def check():
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=4.0, headers=headers) as client:
        for ep in ENDPOINTS:
            try:
                res = await client.get(ep)
                print(f"[OK] {ep} -> Status: {res.status_code}")
            except Exception as e:
                print(f"[FAIL] {ep} -> {e}")

asyncio.run(check())
