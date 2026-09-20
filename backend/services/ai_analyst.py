import httpx
import os
import json
from typing import Dict, Any, List, Optional
from backend.services.ta_engine import analyze_candlesticks
from backend.services.whale_tracker import get_recent_large_trades
from backend.config import GEMINI_API_KEY, OPENAI_API_KEY

def generate_hybrid_signal(symbol: str, timeframe: str, ta_result: Dict[str, Any], whale_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    High-precision quantitative AI reasoning engine.
    Calculates weighted score, targets (TP1/TP2/TP3/SL), and comprehensive Indonesian rationale.
    """
    current_price = ta_result["current_price"]
    indicators = ta_result["indicators"]
    levels = ta_result["levels"]
    signals = ta_result["signals"]
    atr = indicators.get("atr", current_price * 0.02)
    price_decimals = 8 if symbol.upper() == "PEPEUSDT" else 4
    round_price = lambda value: round(value, price_decimals)
    display_price = lambda value: (
        f"{float(value):.8f}" if symbol.upper() == "PEPEUSDT" else str(value)
    )
    
    # Calculate Bullish vs Bearish score
    bullish_score = 0
    bearish_score = 0
    
    for s in signals:
        if s["bias"] == "BULLISH":
            bullish_score += s["weight"]
        elif s["bias"] == "BEARISH":
            bearish_score += s["weight"]
            
    # Factor in Whale flow
    whale_buy_ratio = whale_result.get("whale_buy_ratio", 50.0)
    if whale_buy_ratio >= 70:
        bullish_score += 25
    elif whale_buy_ratio >= 55:
        bullish_score += 15
    elif whale_buy_ratio <= 30:
        bearish_score += 25
    elif whale_buy_ratio <= 45:
        bearish_score += 15
        
    total_score = bullish_score + bearish_score + 1e-6
    net_diff = bullish_score - bearish_score
    
    # Determine signal and confidence
    if net_diff >= 45:
        signal_type = "STRONG BUY"
        confidence = min(96, int(65 + (net_diff * 0.4)))
        action = "LONG"
    elif net_diff >= 20:
        signal_type = "BUY"
        confidence = min(85, int(60 + (net_diff * 0.4)))
        action = "LONG"
    elif net_diff <= -45:
        signal_type = "STRONG SELL"
        confidence = min(96, int(65 + (abs(net_diff) * 0.4)))
        action = "SHORT"
    elif net_diff <= -20:
        signal_type = "SELL"
        confidence = min(85, int(60 + (abs(net_diff) * 0.4)))
        action = "SHORT"
    else:
        signal_type = "NEUTRAL"
        confidence = int(50 + (abs(net_diff) * 0.5))
        action = "WAIT"

    # Price targets calculations based on ATR & Key Support/Resistance
    if action == "LONG":
        entry_low = round_price(current_price * 0.997)
        entry_high = round_price(current_price * 1.002)
        entry_zone = f"${display_price(entry_low)} - ${display_price(entry_high)}"
        
        # Stop loss below support / 1.5 * ATR
        sl_val = round_price(max(current_price - (atr * 1.5), levels["support_1"] * 0.995))
        risk = current_price - sl_val
        
        tp1_val = round_price(current_price + (risk * 1.2))
        tp2_val = round_price(current_price + (risk * 2.0))
        tp3_val = round_price(current_price + (risk * 3.5))
        
        rrr = round((tp2_val - current_price) / (risk + 1e-6), 2)
    elif action == "SHORT":
        entry_low = round_price(current_price * 0.998)
        entry_high = round_price(current_price * 1.003)
        entry_zone = f"${display_price(entry_low)} - ${display_price(entry_high)}"
        
        sl_val = round_price(min(current_price + (atr * 1.5), levels["resistance_1"] * 1.005))
        risk = sl_val - current_price
        
        tp1_val = round_price(current_price - (risk * 1.2))
        tp2_val = round_price(current_price - (risk * 2.0))
        tp3_val = round_price(current_price - (risk * 3.5))
        
        rrr = round((current_price - tp2_val) / (risk + 1e-6), 2)
    else:
        entry_zone = f"${display_price(current_price)}"
        sl_val = round_price(current_price * 0.98)
        tp1_val = round_price(current_price * 1.02)
        tp2_val = round_price(current_price * 1.04)
        tp3_val = round_price(current_price * 1.06)
        rrr = 1.0

    # Build detailed AI analysis narrative (Indonesian)
    key_points = [s["desc"] for s in signals]
    whale_info = f"Aktivitas Whale: {whale_result.get('flow_status', 'N/A')} dengan rasio beli {whale_buy_ratio}%."
    
    rationale_paragraphs = []
    if action == "LONG":
        rationale_paragraphs.append(
            f"Berdasarkan algoritma multi-faktor timeframe {timeframe}, {symbol} membentuk setup konfirmasi akumulasi dengan probabilitas kenaikan {confidence}%."
        )
        rationale_paragraphs.append(
            f"Katalis utama: {', '.join(key_points[:3]) if key_points else 'Momentum positif'}. {whale_info}"
        )
        rationale_paragraphs.append(
            f"Strategi eksekusi: Manfaatkan area entry {entry_zone}. Pasang Stop Loss disiplin di ${display_price(sl_val)} dengan rasio Risk/Reward {rrr}:1 menuju target utama TP2 (${display_price(tp2_val)})."
        )
    elif action == "SHORT":
        rationale_paragraphs.append(
            f"Analisa timeframe {timeframe} mendeteksi tekanan jual kuat pada {symbol} dengan probabilitas penurunan {confidence}%."
        )
        rationale_paragraphs.append(
            f"Katalis utama: {', '.join(key_points[:3]) if key_points else 'Tekanan distribusi'}. {whale_info}"
        )
        rationale_paragraphs.append(
            f"Strategi eksekusi: Ambil posisi Sell/Short di area {entry_zone} dengan batas risiko Stop Loss di ${display_price(sl_val)} dan target TP2 di ${display_price(tp2_val)}."
        )
    else:
        rationale_paragraphs.append(
            f"Kondisi pasar {symbol} pada timeframe {timeframe} sedang dalam fase konsolidasi / sideway tanpa tren dominan (Confidence {confidence}%)."
        )
        rationale_paragraphs.append(
            f"Disarankan 'Wait and See' hingga terjadi breakout valid di atas resistensi ${levels['resistance_1']} atau pantulan di support ${levels['support_1']}."
        )

    ai_rationale = "\n\n".join(rationale_paragraphs)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "signal": signal_type,
        "action": action,
        "confidence": confidence,
        "current_price": current_price,
        "entry_zone": entry_zone,
        "take_profit_1": tp1_val,
        "take_profit_2": tp2_val,
        "take_profit_3": tp3_val,
        "stop_loss": sl_val,
        "risk_reward_ratio": f"1:{rrr}",
        "indicators": indicators,
        "levels": levels,
        "whale_summary": {
            "whale_buy_ratio": whale_buy_ratio,
            "flow_status": whale_result.get("flow_status", "N/A"),
            "whale_trades_count": whale_result.get("whale_trade_count", 0)
        },
        "catalysts": [s["name"] for s in signals],
        "ai_rationale": ai_rationale
    }

async def generate_deep_ai_insights(prompt_data: Dict[str, Any]) -> Optional[str]:
    """
    Optional LLM generation if GEMINI_API_KEY or OPENAI_API_KEY is supplied.
    """
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt = f"Anda adalah AI Senior Trading Terminal Analyst. Berikan analisa teknikal singkat, padat, dan tajam dalam Bahasa Indonesia untuk setup berikut:\n{json.dumps(prompt_data, indent=2)}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"Gemini API Exception: {e}")
            
    return None
