"""
news_provider.py
Google News RSS uzerinden sirket bazli haber basliklarini ceker (ucretsiz,
API anahtari gerekmez) ve basit anahtar kelime eslestirmesiyle
pozitif isaretli olanlari secer.

ONEMLI SINIRLAMA: Bu GERCEK bir yapay zeka/NLP duygu analizi DEGILDIR.
Sadece config.py'deki kelimelerin baslikta gecip gecmedigine bakar:
  - Ironiyi, olumsuzlama eklerini ("...artmadı" gibi) anlamaz.
  - Yanlis pozitif/negatif verebilir.
  - Google News RSS gercek zamanli degildir, birkac saat/gun gecikmeli
    haberler de donebilir.
Bunu "bu basliga bir bak" seviyesinde bir isaret olarak kullan, teknik
sinyal kadar guvenilir bir hesap DEGILDIR - o yuzden ayri etiketleniyor.
"""

import urllib.parse

import feedparser

import config


def _fetch_headlines(company_name, extra_terms=""):
    query = f"{company_name} {extra_terms} {config.NEWS_LOOKBACK_WINDOW}".strip()
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=tr&gl=TR&ceid=TR:tr"
    try:
        feed = feedparser.parse(url)
        return [entry.get("title", "") for entry in feed.entries if entry.get("title")]
    except Exception as exc:
        print(f"[news_provider] Haber cekilemedi ({company_name}): {exc}")
        return []


def _is_positive(headline):
    text = headline.lower()
    has_positive = any(kw.lower() in text for kw in config.NEWS_POSITIVE_KEYWORDS)
    has_negative = any(kw.lower() in text for kw in config.NEWS_NEGATIVE_KEYWORDS)
    return has_positive and not has_negative


def get_positive_headlines(symbol):
    """
    Verilen sembol icin son haber basliklarini tarar, pozitif anahtar
    kelime iceren (ve negatif kelime icermeyen) olanlari dondurur.
    Bos liste = pozitif isaretli haber bulunamadi.
    """
    company_name = config.NEWS_COMPANIES.get(symbol)
    if not company_name:
        return []

    headlines = _fetch_headlines(company_name, "hisse")
    return [h for h in headlines if _is_positive(h)]
