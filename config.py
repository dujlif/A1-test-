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

# --- Strateji Parametreleri ---
# NOT: Bu degerler daha SIK sinyal uretecek sekilde gevsetildi (asagida
# EMA50/200 yerine EMA20/50 kullaniliyor, RSI bandi genisletildi, kesisim
# tespiti son 1 mum yerine son 3 muma bakiyor). Bunun bedeli: daha fazla
# sinyal ama muhtemelen biraz daha fazla yanlis sinyal de demek - siki bir
# EMA50/200 filtresi daha az ama istatistiksel olarak daha "temiz" sinyal
# verirdi. Cok fazla sinyal geliyorsa RSI bandini daraltip/EMA periyotlarini
# uzatarak geri sikilastirabilirsin.
TREND_EMA_FAST = 20
TREND_EMA_SLOW = 50
ENTRY_EMA_FAST = 9
ENTRY_EMA_SLOW = 21
RSI_PERIOD = 14
RSI_LONG_MIN, RSI_LONG_MAX = 35, 75
CROSS_LOOKBACK_CANDLES = 3     # kesisim son kac mum icinde aranacak
ATR_PERIOD = 14
ATR_SL_MULT = 1.5
ATR_TP_MULT = 2.75

# --- Pozisyon Buyuklugu Onerisi (SADECE bilgi amacli, otomatik emir YOK) ---
BUDGET_TRY = 5000.0     # Yaklasik butcen - kendi durumuna gore degistir
RISK_PER_TRADE_PCT = 1.0

# --- Telegram Bildirimi ---
# GitHub Actions'ta calistirirken bu ikisi secret'lardan otomatik okunur.
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

# --- Analist / Banka Onerisi Sinyali (deneysel, YENI) ---
# ONEMLI: BIST icin resmi/ucretsiz bir "analist konsensusu" API'si YOK
# (KAP'in kendi API'si ücretli/kurumsal aboneliğe kapali). Bu yuzden ayni
# Google News RSS yontemiyle, banka/araci kurum adi + tavsiye ifadesi
# birlikte gecen basliklari yakalamaya calisiyoruz. Bu da bir "dikkatini
# buna cek" isareti - resmi/yapilandirilmis bir konsensus verisi degil,
# kaçırdığı ya da yanlış yakaladığı haberler olabilir.
USE_ANALYST_SIGNAL = True

BANK_NAMES = [
    "İş Yatırım", "Is Yatirim", "Ak Yatırım", "Ak Yatirim",
    "Garanti BBVA Yatırım", "Garanti Yatirim", "Yapı Kredi Yatırım",
    "Yapi Kredi Yatirim", "Deniz Yatırım", "Deniz Yatirim",
    "QNB Finansinvest", "QNB Yatırım", "Tacirler Yatırım",
    "Tacirler Yatirim", "Ata Yatırım", "Ata Yatirim", "Vakıf Yatırım",
    "Vakif Yatirim", "Halk Yatırım", "Halk Yatirim", "Şeker Yatırım",
    "Seker Yatirim", "Gedik Yatırım", "Gedik Yatirim", "Oyak Yatırım",
    "Oyak Yatirim", "Integral Yatirim", "Ahlatci Yatirim",
]

ANALYST_RECOMMENDATION_KEYWORDS = [
    "al tavsiyesi", "hedef fiyat yukseltildi", "hedef fiyat yükseltildi",
    "hedef fiyatini yukseltti", "hedef fiyatını yükseltti",
    "endeks uzeri getiri", "endeks üzeri getiri", "topla tavsiyesi",
    "pozitif gorus", "pozitif görüş", "tavsiyesini yineledi",
]

# Haber VE analist taramasi WATCHLIST'ten BAGIMSIZ ve daha genis calisir -
# buradaki her sirket icin taranir, WATCHLIST'te olmasa bile sinyal
# uretilebilir. Kendi eklemek istedigin sirket varsa ayni formatta
# ekleyebilirsin: "TICKER.IS": "Google'da aratilacak sirket adi"
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
