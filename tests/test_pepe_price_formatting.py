import unittest

from backend.services.ai_analyst import generate_hybrid_signal
from backend.services.telegram_bot import format_progress_message, format_signal_message


class PepePriceFormattingTests(unittest.TestCase):
    def _signal(self):
        ta_result = {
            "current_price": 0.00000401,
            "indicators": {"atr": 0.00000008},
            "levels": {"support_1": 0.00000391, "resistance_1": 0.00000412},
            "signals": [
                {"name": "RSI Bullish Momentum", "bias": "BULLISH", "weight": 50, "desc": "test"}
            ],
        }
        return generate_hybrid_signal(
            "PEPEUSDT", "1h", ta_result,
            {"whale_buy_ratio": 70, "flow_status": "NET ACCUMULATION"},
        )

    def test_pepe_signal_uses_fixed_eight_decimal_prices(self):
        signal = self._signal()
        message = format_signal_message(signal)

        self.assertIn("$0.00000401", message)
        self.assertIn("Entry Zone:</b> <code>$0.00000400 - $0.00000402", message)
        self.assertNotRegex(message.lower(), r"\d(?:\.\d+)?e-\d")
        self.assertNotIn("$0.0</code>", message)

    def test_pepe_progress_price_is_not_scientific_notation(self):
        item = {
            "symbol": "PEPEUSDT", "action": "LONG", "status": "TP1_HIT",
            "checklist": {"tp1_reached": True},
        }
        message = format_progress_message(item, "TP1", 0.00000401)
        self.assertIn("$0.00000401", message)
        self.assertNotRegex(message.lower(), r"\d(?:\.\d+)?e-\d")

    def test_other_symbol_display_remains_unchanged(self):
        item = {
            "symbol": "BTCUSDT", "action": "LONG", "status": "TP1_HIT",
            "checklist": {"tp1_reached": True},
        }
        self.assertIn("$78123.5", format_progress_message(item, "TP1", 78123.5))


if __name__ == "__main__":
    unittest.main()
