"""
strategy.py
EMA trend filtresi + EMA/RSI giris sinyali + ATR tabanli stop/hedef.
Veri kaynagi BIST/yfinance.

ONEMLI FARK: Bu bot SADECE AL (long) sinyali uretir. BIST'te aciga satis
(short) islemi kucuk butceli bireysel yatirimcilar icin genelde erisilebilir
degildir. Bu yuzden gunluk trend asagi yonluyse bot sadece "bu hissede
firsat yok" der, satis sinyali uretmeye calismaz.

NOT (guncelleme): Daha SIK sinyal uretmesi icin trend filtresi EMA20/EMA50'ye
hizlandirildi, RSI bandi genisletildi, ve kesisim tespiti sadece son mum
yerine son birkac mum icinde araniyor (config.CROSS_LOOKBACK_CANDLES).
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
    result = 100 - (100 / (1 + rs))
    # avg_loss tam olarak 0 ise (son periyotta hic dusus yok) ve avg_gain > 0
    # ise RSI = 100 kabul edilir (aksi halde 0/0 -> NaN donup sinyal kaybolurdu)
    result = result.mask((avg_loss == 0) & (avg_gain > 0), 100)
    return result


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
    """EMA20/EMA50: 1 = yukselen trend, -1 = dusen trend, 0 = belirsiz."""
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
    Sadece gunluk trend YUKSELEN oldugunda, saatlik EMA9/EMA21'in son
    CROSS_LOOKBACK_CANDLES mum icinde yukari kesmis olmasi + RSI filtresiyle
    AL sinyali arar.
    Donus: ("AL", son_mum_zamani) veya (None, None)
    """
    if daily_trend != 1:
        return None, None

    df = data_provider.get_hourly(symbol)
    min_needed = config.ENTRY_EMA_SLOW + config.CROSS_LOOKBACK_CANDLES + 1
    if df is None or len(df) < min_needed:
        return None, None

    fast = ema(df["close"], config.ENTRY_EMA_FAST)
    slow = ema(df["close"], config.ENTRY_EMA_SLOW)
    rsi_vals = rsi(df["close"], config.RSI_PERIOD)

    # Su an fast > slow mu (yukselen momentum) VE son CROSS_LOOKBACK_CANDLES
    # mum icinde bir "asagidan yukariya gecis" ani oldu mu?
    above = fast > slow
    prev_above = above.shift(1, fill_value=False)  # fill_value ile bool dtype korunur (NaN -> object/bitwise-not hatasi onlenir)
    lookback = config.CROSS_LOOKBACK_CANDLES
    window_above = above.iloc[-(lookback + 1):]
    window_prev = prev_above.iloc[-(lookback + 1):]
    fresh_cross = bool((window_above & ~window_prev).any())
    currently_above = bool(fast.iloc[-1] > slow.iloc[-1])

    last_rsi = rsi_vals.iloc[-1]

    time_col = "datetime" if "datetime" in df.columns else df.columns[0]
    last_candle_time = df[time_col].iloc[-1]

    if currently_above and fresh_cross and config.RSI_LONG_MIN <= last_rsi <= config.RSI_LONG_MAX:
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
