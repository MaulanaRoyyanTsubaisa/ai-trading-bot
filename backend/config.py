import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# AI Reasoning Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Trading & Scanning Defaults
DEFAULT_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "NEARUSDT",
    "LINKUSDT",
    "SUIUSDT",
    "PEPEUSDT"
]

DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "1h")
MIN_CONFIDENCE_ALERT = int(os.getenv("MIN_CONFIDENCE_ALERT", "70"))
SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "5"))

# Whale Tracker Settings
WHALE_VOLUME_MULTIPLIER = float(os.getenv("WHALE_VOLUME_MULTIPLIER", "2.2"))
WHALE_MIN_USD_VALUE = float(os.getenv("WHALE_MIN_USD_VALUE", "50000"))

# Server Settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
