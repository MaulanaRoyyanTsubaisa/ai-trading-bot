import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd": macd_line,
        "signal": signal_line,
        "hist": histogram
    }

def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    bandwidth = (upper - lower) / (middle + 1e-10) * 100
    percent_b = (series - lower) / (upper - lower + 1e-10)
    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
        "bandwidth": bandwidth,
        "percent_b": percent_b
    }

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['high']
    low = df['low']
    close = df['close']
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    return atr

def calculate_cmf(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Chaikin Money Flow (CMF) measures institutional Accumulation/Distribution.
    """
    high = df['high']
    low = df['low']
    close = df['close']
    volume = df['volume']
    
    mf_multiplier = ((close - low) - (high - close)) / (high - low + 1e-10)
    mf_volume = mf_multiplier * volume
    cmf = mf_volume.rolling(window=period).sum() / (volume.rolling(window=period).sum() + 1e-10)
    return cmf

def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Dict[str, Any]:
    atr = calculate_atr(df, period)
    hl2 = (df['high'] + df['low']) / 2
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)
    
    supertrend = [True] * len(df) # True = Bullish, False = Bearish
    trend_values = [0.0] * len(df)
    
    for i in range(1, len(df)):
        curr_close = df['close'].iloc[i]
        prev_close = df['close'].iloc[i-1]
        
        # Adjust upper band
        if upper_band.iloc[i] < upper_band.iloc[i-1] or prev_close > upper_band.iloc[i-1]:
            upper_band.iloc[i] = upper_band.iloc[i]
        else:
            upper_band.iloc[i] = upper_band.iloc[i-1]
            
        # Adjust lower band
        if lower_band.iloc[i] > lower_band.iloc[i-1] or prev_close < lower_band.iloc[i-1]:
            lower_band.iloc[i] = lower_band.iloc[i]
        else:
            lower_band.iloc[i] = lower_band.iloc[i-1]
            
        if curr_close > upper_band.iloc[i-1]:
            supertrend[i] = True
        elif curr_close < lower_band.iloc[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
            
        val = trend_values[i]
        if np.isnan(val):
            val = curr_close * 0.98 if supertrend[i] else curr_close * 1.02
        trend_values[i] = val
        
    final_st_val = float(trend_values[-1])
    if np.isnan(final_st_val):
        final_st_val = float(df['close'].iloc[-1]) * 0.98
        
    return {
        "is_bullish": supertrend[-1],
        "supertrend_value": round(final_st_val, 4)
    }

def analyze_candlesticks(candles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Full technical analysis suite on candle data.
    """
    if len(candles) < 30:
        return {"error": "Insufficient candle data"}
        
    df = pd.DataFrame(candles)
    
    # Calculate indicators
    df['rsi'] = calculate_rsi(df['close'], period=14)
    
    macd_dict = calculate_macd(df['close'])
    df['macd'] = macd_dict['macd']
    df['macd_signal'] = macd_dict['signal']
    df['macd_hist'] = macd_dict['hist']
    
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean() if len(df) >= 200 else df['close'].ewm(span=len(df), adjust=False).mean()
    
    bb_dict = calculate_bollinger_bands(df['close'])
    df['bb_upper'] = bb_dict['upper']
    df['bb_middle'] = bb_dict['middle']
    df['bb_lower'] = bb_dict['lower']
    df['bb_bandwidth'] = bb_dict['bandwidth']
    df['bb_percent'] = bb_dict['percent_b']
    
    df['atr'] = calculate_atr(df, period=14)
    df['cmf'] = calculate_cmf(df, period=20)
    
    # Supertrend
    st_res = calculate_supertrend(df)
    
    # Volume moving averages
    df['vol_ma20'] = df['volume'].rolling(window=20).mean()
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    current_price = float(last['close'])
    volume_ratio = float(last['volume'] / (last['vol_ma20'] + 1e-10)) if not pd.isna(last['vol_ma20']) else 1.0
    
    # Support & Resistance via Pivot / Swings
    recent_highs = df['high'].iloc[-20:].max()
    recent_lows = df['low'].iloc[-20:].min()
    
    pivot = (last['high'] + last['low'] + last['close']) / 3
    r1 = (2 * pivot) - last['low']
    s1 = (2 * pivot) - last['high']
    r2 = pivot + (last['high'] - last['low'])
    s2 = pivot - (last['high'] - last['low'])
    
    # Technical Summary Scores
    signals = []
    
    # RSI Condition
    rsi_val = float(last['rsi'])
    if rsi_val <= 30:
        signals.append({"name": "RSI Oversold", "bias": "BULLISH", "weight": 20, "desc": f"RSI di {rsi_val:.1f} (Zona jenuh jual, potensi reversal naik)"})
    elif rsi_val >= 70:
        signals.append({"name": "RSI Overbought", "bias": "BEARISH", "weight": 20, "desc": f"RSI di {rsi_val:.1f} (Zona jenuh beli, potensi koreksi turun)"})
    elif 50 <= rsi_val < 70:
        signals.append({"name": "RSI Bullish Momentum", "bias": "BULLISH", "weight": 10, "desc": f"RSI di {rsi_val:.1f} dalam momentum positif"})
    else:
        signals.append({"name": "RSI Bearish Momentum", "bias": "BEARISH", "weight": 10, "desc": f"RSI di {rsi_val:.1f} dalam momentum negatif"})
        
    # MACD Condition
    macd_hist = float(last['macd_hist'])
    prev_macd_hist = float(prev['macd_hist'])
    if macd_hist > 0 and prev_macd_hist <= 0:
        signals.append({"name": "MACD Golden Cross", "bias": "BULLISH", "weight": 25, "desc": "Histogram MACD memotong ke atas level nol (Konfirmasi Bullish Cross)"})
    elif macd_hist < 0 and prev_macd_hist >= 0:
        signals.append({"name": "MACD Death Cross", "bias": "BEARISH", "weight": 25, "desc": "Histogram MACD memotong ke bawah level nol (Konfirmasi Bearish Cross)"})
    elif macd_hist > 0:
        signals.append({"name": "MACD Bullish Histogram", "bias": "BULLISH", "weight": 10, "desc": "MACD bertahan di area positif"})
    else:
        signals.append({"name": "MACD Bearish Histogram", "bias": "BEARISH", "weight": 10, "desc": "MACD berada di area negatif"})

    # EMA Alignment
    ema20 = float(last['ema20'])
    ema50 = float(last['ema50'])
    ema200 = float(last['ema200'])
    
    if current_price > ema20 > ema50:
        signals.append({"name": "EMA Bullish Alignment", "bias": "BULLISH", "weight": 20, "desc": "Harga di atas EMA20 & EMA50 (Trend Bullish Kuat)"})
    elif current_price < ema20 < ema50:
        signals.append({"name": "EMA Bearish Alignment", "bias": "BEARISH", "weight": 20, "desc": "Harga di bawah EMA20 & EMA50 (Trend Bearish Kuat)"})
        
    # SuperTrend
    if st_res["is_bullish"]:
        signals.append({"name": "SuperTrend Bullish", "bias": "BULLISH", "weight": 15, "desc": f"SuperTrend menunjukkan sinyal Buy (Support di {st_res['supertrend_value']})"})
    else:
        signals.append({"name": "SuperTrend Bearish", "bias": "BEARISH", "weight": 15, "desc": f"SuperTrend menunjukkan sinyal Sell (Resistensi di {st_res['supertrend_value']})"})
        
    # Volume Anomaly
    if volume_ratio >= 2.0:
        if current_price > float(prev['close']):
            signals.append({"name": "Bullish Volume Spike", "bias": "BULLISH", "weight": 20, "desc": f"Lonjakan volume {volume_ratio:.2f}x rata-rata didukung dorongan harga naik"})
        else:
            signals.append({"name": "Bearish Volume Spike", "bias": "BEARISH", "weight": 20, "desc": f"Lonjakan tekanan jual dengan volume {volume_ratio:.2f}x"})

    # Chaikin Money Flow (Whale Accumulation / Distribution)
    cmf_val = float(last['cmf']) if not pd.isna(last['cmf']) else 0.0
    if cmf_val > 0.1:
        signals.append({"name": "Whale Inflow (CMF > 0.1)", "bias": "BULLISH", "weight": 15, "desc": f"Aliran dana masuk/akumulasi terdeteksi (CMF: {cmf_val:.2f})"})
    elif cmf_val < -0.1:
        signals.append({"name": "Whale Outflow (CMF < -0.1)", "bias": "BEARISH", "weight": 15, "desc": f"Aliran distribusi dana keluar terdeteksi (CMF: {cmf_val:.2f})"})

    return {
        "current_price": current_price,
        "indicators": {
            "rsi": round(rsi_val, 2),
            "macd": round(float(last['macd']), 4),
            "macd_signal": round(float(last['macd_signal']), 4),
            "macd_hist": round(macd_hist, 4),
            "ema20": round(ema20, 4),
            "ema50": round(ema50, 4),
            "ema200": round(ema200, 4),
            "bb_upper": round(float(last['bb_upper']), 4),
            "bb_middle": round(float(last['bb_middle']), 4),
            "bb_lower": round(float(last['bb_lower']), 4),
            "bb_bandwidth": round(float(last['bb_bandwidth']), 2),
            "atr": round(float(last['atr']), 4),
            "cmf": round(cmf_val, 4),
            "supertrend_bullish": st_res["is_bullish"],
            "supertrend_value": st_res["supertrend_value"],
            "volume_ratio": round(volume_ratio, 2)
        },
        "levels": {
            "support_1": round(s1, 4),
            "support_2": round(s2, 4),
            "resistance_1": round(r1, 4),
            "resistance_2": round(r2, 4),
            "recent_high": round(float(recent_highs), 4),
            "recent_low": round(float(recent_lows), 4)
        },
        "signals": signals
    }
