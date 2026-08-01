"""
data_provider.py
BIST fiyat verisi - yfinance uzerinden, ucretsiz ve API anahtari gerektirmez.

NOT: Veri, gercek zamanli borsa akisina gore birkac dakika gecikmeli
olabilir. Yuksek frekansli/saniyelik islemler icin uygun degildir,
gunluk-saatlik strateji icin yeterlidir.
"""

import yfinance as yf

import config


def _clean(df):
    if df is None or df.empty:
        return None
    df = df.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    return df


def get_daily(symbol):
    df = yf.Ticker(symbol).history(period=config.DAILY_PERIOD, interval=config.DAILY_INTERVAL)
    return _clean(df)


def get_hourly(symbol):
    df = yf.Ticker(symbol).history(period=config.HOURLY_PERIOD, interval=config.HOURLY_INTERVAL)
    return _clean(df)
