"""
config.py - BIST Sinyal Botu ayarlari
"""

import os

# --- Takip Listesi ---
# yfinance formatinda BIST ticker'lari (.IS eki ile). Istedigin kadar
# hisse ekleyip cikarabilirsin.
WATCHLIST = [
    "THYAO.IS", "GARAN.IS", "ASELS.IS", "KCHOL.IS",
    "EREGL.IS", "SASA.IS", "BIMAS.IS", "TUPRS.IS",
]

# --- Veri Araliklari ---
DAILY_PERIOD = "2y"
DAILY_INTERVAL = "1d"
HOURLY_PERIOD = "60d"
HOURLY_INTERVAL = "60m"

# --- Strateji Parametreleri (forex botuyla ayni mantik) ---
TREND_EMA_FAST = 50
TREND_EMA_SLOW = 200
ENTRY_EMA_FAST = 9
ENTRY_EMA_SLOW = 21
RSI_PERIOD = 14
RSI_LONG_MIN, RSI_LONG_MAX = 40, 70
ATR_PERIOD = 14
ATR_SL_MULT = 1.5
ATR_TP_MULT = 2.75

# --- Pozisyon Buyuklugu Onerisi (SADECE bilgi amacli, otomatik emir YOK) ---
BUDGET_TRY = 5000.0     # Yaklasik butcen - kendi durumuna gore degistir
RISK_PER_TRADE_PCT = 1.0

# --- Telegram Bildirimi ---
# GitHub Actions'ta calistirirken bu ikisi secret'lardan otomatik okunur.
# Termux'ta yerel test icin istersen elle de yazabilirsin (guvenli degil,
# sadece kendi telefonunda test ederken).
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
USE_TELEGRAM = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# --- Calisma Modu ---
# RUN_ONCE=true  -> bir kere kontrol edip cikar (GitHub Actions icin varsayilan)
# RUN_ONCE=false -> sonsuz donguyle calisir (Termux'ta acik tutmak icin)
RUN_ONCE = os.environ.get("RUN_ONCE", "true").lower() != "false"
LOOP_SLEEP_SECONDS = 300     # sadece RUN_ONCE=false oldugunda kullanilir
SIGNAL_LOG_FILE = "signals_log.csv"
STATE_FILE = "state.json"
