"""
config.py - BIST Sinyal Botu ayarlari
"""

import os

# --- Takip Listesi ---
# yfinance formatinda BIST ticker'lari (.IS eki ile). Istedigin kadar
# hisse ekleyip cikarabilirsin. BIST30/50 agirlikli, likit ~40 hisse.
WATCHLIST = [
    "THYAO.IS", "GARAN.IS", "AKBNK.IS", "ISCTR.IS", "YKBNK.IS",
    "HALKB.IS", "VAKBN.IS", "ASELS.IS", "KCHOL.IS", "SAHOL.IS",
    "EREGL.IS", "KRDMD.IS", "SASA.IS", "PETKM.IS", "TUPRS.IS",
    "BIMAS.IS", "MGROS.IS", "ULKER.IS", "CCOLA.IS", "AEFES.IS",
    "TCELL.IS", "TTKOM.IS", "PGSUS.IS", "FROTO.IS", "TOASO.IS",
    "ARCLK.IS", "VESTL.IS", "SISE.IS", "KOZAL.IS", "KOZAA.IS",
    "ENKAI.IS", "TAVHL.IS", "DOHOL.IS", "EKGYO.IS", "GUBRF.IS",
    "ALARK.IS", "TKFEN.IS", "BRSAN.IS", "ASTOR.IS", "OYAKC.IS",
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

# Piyasa kapaliyken de test icin zorla calistirmak istersen (GitHub Actions
# "Run workflow" ekranindaki force_run kutusundan otomatik ayarlanir).
FORCE_RUN = os.environ.get("FORCE_RUN", "false").lower() == "true"

# --- Haber Tabanli Sinyal (deneysel) ---
# ONEMLI: Bu GERCEK bir yapay zeka/NLP duygu analizi DEGILDIR. Sadece
# haber basliginda belirlenen kelimelerin gecip gecmedigine bakar. Yanlis
# pozitif verebilir - "bu haberi oku" seviyesinde bir isaret olarak gor,
# kesin hukum olarak degil. Kapatmak icin False yap.
USE_NEWS_SIGNAL = True
NEWS_LOOKBACK_WINDOW = "when:2d"   # Google News RSS zaman filtresi

NEWS_POSITIVE_KEYWORDS = [
    "rekor", "kar artisi", "kâr artışı", "yukseldi", "yükseldi",
    "anlasma imzaladi", "anlaşma imzaladı", "sozlesme imzaladi",
    "sözleşme imzaladı", "ihale kazandi", "ihale kazandı",
    "yeni yatirim", "yeni yatırım", "temettu", "temettü",
    "buyume", "büyüme", "ihracat rekoru", "hedef fiyat yukseltildi",
    "hedef fiyat yükseltildi", "tavan yapti", "tavan yaptı",
    "prim yapti", "prim yaptı",
]
NEWS_NEGATIVE_KEYWORDS = [
    "zarar", "dava acildi", "dava açıldı", "sorusturma", "soruşturma",
    "dustu", "düştü", "kriz", "iflas", "ceza kesildi", "taban yapti",
    "taban yaptı", "iptal edildi", "uretim durdu", "üretim durdu",
    "greve gitti", "temerrut", "temerrüt",
]

# Haber taramasi WATCHLIST'ten BAGIMSIZ ve daha genis calisir - buradaki
# her sirket icin haber taranir, WATCHLIST'te olmasa bile pozitif haber
# cikarsa sinyal uretilir. Kendi eklemek istedigin sirket varsa ayni
# formatta ekleyebilirsin: "TICKER.IS": "Google'da aratilacak sirket adi"
NEWS_COMPANIES = {
    "THYAO.IS": "Türk Hava Yolları", "GARAN.IS": "Garanti BBVA",
    "AKBNK.IS": "Akbank", "ISCTR.IS": "İş Bankası",
    "YKBNK.IS": "Yapı Kredi", "HALKB.IS": "Halkbank",
    "VAKBN.IS": "VakıfBank", "ASELS.IS": "Aselsan",
    "KCHOL.IS": "Koç Holding", "SAHOL.IS": "Sabancı Holding",
    "EREGL.IS": "Erdemir", "KRDMD.IS": "Kardemir",
    "SASA.IS": "Sasa Polyester", "PETKM.IS": "Petkim",
    "TUPRS.IS": "Tüpraş", "BIMAS.IS": "BİM",
    "MGROS.IS": "Migros", "ULKER.IS": "Ülker",
    "CCOLA.IS": "Coca-Cola İçecek", "AEFES.IS": "Anadolu Efes",
    "TCELL.IS": "Turkcell", "TTKOM.IS": "Türk Telekom",
    "PGSUS.IS": "Pegasus", "FROTO.IS": "Ford Otosan",
    "TOASO.IS": "Tofaş", "ARCLK.IS": "Arçelik",
    "VESTL.IS": "Vestel", "SISE.IS": "Şişecam",
    "KOZAL.IS": "Koza Altın", "KOZAA.IS": "Koza Madencilik",
    "ENKAI.IS": "Enka İnşaat", "TAVHL.IS": "TAV Havalimanları",
    "DOHOL.IS": "Doğan Holding", "EKGYO.IS": "Emlak Konut",
    "GUBRF.IS": "Gübre Fabrikaları", "ALARK.IS": "Alarko Holding",
    "TKFEN.IS": "Tekfen Holding", "BRSAN.IS": "Borusan Mannesmann",
    "ASTOR.IS": "Astor Enerji", "OYAKC.IS": "Oyak Çimento",
}
