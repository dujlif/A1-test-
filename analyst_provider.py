"""
analyst_provider.py
Banka/araci kurum analist tavsiyelerini (AL tavsiyesi, hedef fiyat
yukseltme vb.) yakalamaya calisir. Ayni yontem news_provider.py ile ayni
(Google News RSS - ucretsiz, API anahtari gerekmez), ama sorgu ve anahtar
kelimeler analist/banka tavsiyelerine odaklanmis.

ONEMLI SINIRLAMA: BIST icin resmi/yapilandirilmis, ucretsiz bir "analist
konsensusu" API'si YOKTUR (KAP'in kendi API'si ucretli/kurumsal aboneliğe
kapali, TradingView gibi sitelerdeki veriler de kendi kapali sistemleri).
Bu modul, haber basliklarinda banka/kurum adi + tavsiye ifadesi BIRLIKTE
gecen basliklari YAKALAMAYA CALISAN bir arama katmanidir - resmi/dogrulanmis
bir konsensus verisi degildir. Kaciran ya da yanlis yakalayan durumlar olur.
"""

import config
import news_provider


def _mentions_bank_recommendation(headline):
    text = headline.lower()
    has_bank = any(bank.lower() in text for bank in config.BANK_NAMES)
    has_reco = any(kw.lower() in text for kw in config.ANALYST_RECOMMENDATION_KEYWORDS)
    return has_bank and has_reco


def get_recommendation_headlines(symbol):
    """
    Verilen sembol icin, banka/kurum adi + tavsiye ifadesi birlikte gecen
    baslıkları dondurur. Bos liste = yakalanan bir sey yok (bu, tavsiye
    olmadigi anlamina gelmez - sadece haber aramasinda yakalanmadi demektir).
    """
    company_name = config.NEWS_COMPANIES.get(symbol)
    if not company_name:
        return []

    headlines = news_provider._fetch_headlines(company_name, "hedef fiyat OR tavsiye")
    return [h for h in headlines if _mentions_bank_recommendation(h)]
