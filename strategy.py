"""
strategy.py
Forex botuyla ayni matematik (EMA trend filtresi + EMA/RSI giris sinyali +
ATR tabanli stop/hedef), veri kaynagi BIST/yfinance.

ONEMLI FARK: Bu bot SADECE AL (long) sinyali uretir. BIST'te aciga satis
(short) islemi kucuk butceli bireysel yatirimcilar icin genelde erisilebilir
degildir (ayri sozlesme, ek teminat gerektirir). Bu yuzden gunluk trend
asagi yonluyse bot sadece "bu hissede firsat yok" der, satis sinyali
uretmeye calismaz.
"""

import numpy as np
import pandas as pd

import config
import data_provider


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def atr(df, period):
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def get_daily_trend(symbol):
    """D1 EMA50/EMA200: 1 = yukselen trend, -1 = dusen trend, 0 = belirsiz."""
    df = data_provider.get_daily(symbol)
    if df is None or len(df) < config.TREND_EMA_SLOW + 1:
        return 0
    fast = ema(df["close"], config.TREND_EMA_FAST)
    slow = ema(df["close"], config.TREND_EMA_SLOW)
    if fast.iloc[-1] > slow.iloc[-1]:
        return 1
    if fast.iloc[-1] < slow.iloc[-1]:
        return -1
    return 0


def get_entry_signal(symbol, daily_trend):
    """
    Sadece gunluk trend YUKSELEN oldugunda, saatlik EMA9/EMA21 yukari
    kesisimi + RSI filtresiyle AL sinyali arar.
    Donus: ("AL", son_mum_zamani) veya (None, None)
    """
    if daily_trend != 1:
        return None, None

    df = data_provider.get_hourly(symbol)
    if df is None or len(df) < config.ENTRY_EMA_SLOW + 2:
        return None, None

    fast = ema(df["close"], config.ENTRY_EMA_FAST)
    slow = ema(df["close"], config.ENTRY_EMA_SLOW)
    rsi_vals = rsi(df["close"], config.RSI_PERIOD)

    crossed_up = fast.iloc[-2] <= slow.iloc[-2] and fast.iloc[-1] > slow.iloc[-1]
    last_rsi = rsi_vals.iloc[-1]

    time_col = "datetime" if "datetime" in df.columns else df.columns[0]
    last_candle_time = df[time_col].iloc[-1]

    if crossed_up and config.RSI_LONG_MIN <= last_rsi <= config.RSI_LONG_MAX:
        return "AL", last_candle_time
    return None, None


def get_atr_value(symbol):
    df = data_provider.get_hourly(symbol)
    if df is None or len(df) < config.ATR_PERIOD + 1:
        return None
    atr_series = atr(df, config.ATR_PERIOD)
    return atr_series.iloc[-1]


def get_last_price(symbol):
    df = data_provider.get_hourly(symbol)
    if df is None or df.empty:
        return None
    return df["close"].iloc[-1]
