import unittest
from unittest.mock import AsyncMock, patch

from backend.services import signal_tracker, telegram_bot


class _Response:
    status_code = 200
    text = "ok"

    def json(self):
        return {"ok": True, "result": {"message_id": 77}}


class _Client:
    payload = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, json):
        _Client.payload = json
        return _Response()


class TelegramReplyTests(unittest.IsolatedAsyncioTestCase):
    async def test_reply_uses_original_message_id(self):
        with (
            patch.object(telegram_bot, "TELEGRAM_BOT_TOKEN", "test-token"),
            patch.object(telegram_bot, "TELEGRAM_CHAT_ID", "123"),
            patch.object(telegram_bot.httpx, "AsyncClient", _Client),
        ):
            message_id = await telegram_bot.send_telegram_message("TP1 hit", reply_to_message_id=42)

        self.assertEqual(message_id, 77)
        self.assertEqual(_Client.payload["reply_parameters"]["message_id"], 42)
        self.assertTrue(_Client.payload["reply_parameters"]["allow_sending_without_reply"])

    async def test_new_levels_are_emitted_once_in_order(self):
        item = {
            "id": "AAA_1",
            "symbol": "AAAUSDT",
            "action": "LONG",
            "entry_price": 100.0,
            "tp1": 102.0,
            "tp2": 104.0,
            "tp3": 108.0,
            "sl": 96.0,
            "status": "IN_PROGRESS",
            "closed_at": None,
            "current_price": 100.0,
            "pnl_percent": 0.0,
            "max_gain_percent": 0.0,
            "checklist": {
                "entry_filled": True,
                "tp1_reached": False,
                "tp2_reached": False,
                "tp3_reached": False,
                "sl_triggered": False,
            },
        }
        item["telegram_message_id"] = 42
        item["telegram_notified_levels"] = []
        signal_tracker.tracked_signals = [item]

        prices = [{"symbol": "AAAUSDT", "price": 105.0}]
        with (
            patch.object(signal_tracker, "get_ticker_24h", AsyncMock(return_value=prices)),
            patch.object(signal_tracker, "_save_state"),
        ):
            await signal_tracker.update_tracked_signals()
            first = signal_tracker.get_pending_progress_events()
            for event in first:
                signal_tracker.mark_progress_notified(item["id"], event["level"])
            await signal_tracker.update_tracked_signals()
            second = signal_tracker.get_pending_progress_events()

        self.assertEqual([event["level"] for event in first], ["TP1", "TP2"])
        self.assertEqual(second, [])
        self.assertEqual(item["status"], "TP2_HIT")


if __name__ == "__main__":
    unittest.main()
