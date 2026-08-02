"""
watcher.py
BIST Trend + Momentum SINYAL Botu - ana calistirma dosyasi.

ONEMLI - forex botundan farki:
  - OTOMATIK EMIR GONDERMEZ. Su an (2026 ortasi) Turkiye'de bireysel
    yatirimcinin ucretsiz/uygun fiyatli kullanabilecegi bir BIST
    algoritmik islem API'si yok (Algolab, Aralik 2025'te kapandi;
    MetaTrader 5 de BIST hisse senedini desteklemiyor). Bu yuzden bot
    SINYAL uretir, islemi SEN kendi araci kurumunun uygulamasindan
    (Midas, Is Yatirim, Gedik, N Kolay vb.) MANUEL olarak yaparsin.
  - Bu sayede minimum tutar siniri da yok - bir payin fiyati kadar
    butceyle baslayabilirsin.

IKI FARKLI SINYAL TIPI URETIR:
  - "AL sinyali"                -> WATCHLIST'teki hisseler icin, EMA/RSI
    teknik hesabina dayanir (guvenilirligi daha yuksek, kural tabanli).
  - "AL sinyali (haber bazli)"  -> NEWS_COMPANIES'teki (cok daha genis)
    hisseler icin, basit anahtar kelime eslestirmesiyle "olumlu gorunen"
    basliklar bulununca uretilir. Bu DENEYSEL ve GERCEK bir NLP analizi
    DEGILDIR - o yuzden ayri etiketleniyor, teknik sinyalle karistirma.

ANDROID KULLANIMI: Telefonun bilgisayar gibi Python calistiramadigi icin
bu script iki modda calisabilir (config.py > RUN_ONCE ile secilir):
  - RUN_ONCE=true  (varsayilan): GitHub Actions gibi bir bulut ortaminda
    saatte bir tetiklenir, kontrol eder, Telegram'a bildirim atar, cikar.
  - RUN_ONCE=false: Termux uygulamasiyla telefonun uzerinde surekli
    calistirmak istersen (sinirli/pilli kullanim icin).

Kar garantisi YOKTUR. Sinyalleri kendi gozlemlerinle karsilastirmadan
uygulama - ozellikle haber bazli olanlari, kaynak basligi kendin de oku.
"""

import csv
import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import config
import news_provider
import notifier
import position_sizer
import strategy

TR_TZ = ZoneInfo("Europe/Istanbul")


def load_state():
    if os.path.isfile(config.STATE_FILE):
        with open(config.STATE_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data.setdefault("technical", {})
    data.setdefault("news", {})
    return data


def save_state(state):
    with open(config.STATE_FILE, "w") as f:
        json.dump(state, f, default=str, ensure_ascii=False)


def log_signal(row):
    file_exists = os.path.isfile(config.SIGNAL_LOG_FILE)
    with open(config.SIGNAL_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["zaman", "sembol", "tur", "detay"])
        writer.writerow(row)


def is_market_open():
    now = datetime.now(TR_TZ)
    if now.weekday() >= 5:  # 5=Cumartesi, 6=Pazar
        return False
    current = now.strftime("%H:%M")
    return "10:00" <= current <= "18:10"


def process_symbol(symbol, state):
    """Teknik (EMA/RSI) AL sinyali - WATCHLIST icin."""
    daily_trend = strategy.get_daily_trend(symbol)
    signal, candle_time = strategy.get_entry_signal(symbol, daily_trend)
    if signal is None:
        return

    candle_key = str(candle_time)
    if state["technical"].get(symbol) == candle_key:
        return  # bu mum icin zaten sinyal verildi, tekrar uyarma

    atr_value = strategy.get_atr_value(symbol)
    price = strategy.get_last_price(symbol)
    if not atr_value or not price:
        return

    sl_price = price - (atr_value * config.ATR_SL_MULT)
    tp_price = price + (atr_value * config.ATR_TP_MULT)
    shares = position_sizer.suggest_shares(price, sl_price)

    message = (
        f"[{symbol}] AL sinyali (teknik)\n"
        f"Fiyat: {price:.2f} TL\n"
        f"Stop: {sl_price:.2f} TL | Hedef: {tp_price:.2f} TL\n"
        f"Onerilen adet (bilgi amacli, {config.BUDGET_TRY:.0f} TL butceye gore): {shares}"
    )
    print(message)
    log_signal([datetime.now(), symbol, "teknik",
                f"fiyat={price:.2f} sl={sl_price:.2f} tp={tp_price:.2f} adet={shares}"])
    notifier.send(message)

    state["technical"][symbol] = candle_key


def process_news(symbol, state):
    """Haber bazli, DENEYSEL AL sinyali - NEWS_COMPANIES icin (WATCHLIST'ten bagimsiz)."""
    positive_headlines = news_provider.get_positive_headlines(symbol)
    if not positive_headlines:
        return

    already_seen = state["news"].setdefault(symbol, [])
    new_headlines = [h for h in positive_headlines if h not in already_seen]
    if not new_headlines:
        return

    headline_block = "\n".join(f"- {h}" for h in new_headlines[:3])
    message = (
        f"[{symbol}] AL sinyali (haber bazli, DENEYSEL)\n"
        f"Pozitif anahtar kelime iceren basliklar:\n{headline_block}\n"
        f"Not: Basit kelime eslestirmesi, gercek analiz degil. "
        f"Haberi kendi gozunle de oku, teknik sinyal kadar guvenilir sayma."
    )
    print(message)
    log_signal([datetime.now(), symbol, "haber", " | ".join(new_headlines[:3])])
    notifier.send(message)

    already_seen.extend(new_headlines)
    state["news"][symbol] = already_seen[-20:]  # sonsuza kadar buyumesin


def run_cycle(state):
    if not (config.FORCE_RUN or is_market_open()):
        print("Piyasa kapali.")
        return

    for symbol in config.WATCHLIST:
        try:
            process_symbol(symbol, state)
        except Exception as exc:
            print(f"[{symbol}] Hata: {exc}")

    if config.USE_NEWS_SIGNAL:
        for symbol in config.NEWS_COMPANIES:
            try:
                process_news(symbol, state)
            except Exception as exc:
                print(f"[{symbol}] Haber hatasi: {exc}")

    save_state(state)


def main():
    state = load_state()
    print("BIST Sinyal Botu baslatildi.")
    print("Teknik takip listesi:", ", ".join(config.WATCHLIST))
    if config.USE_NEWS_SIGNAL:
        print("Haber taramasi:", len(config.NEWS_COMPANIES), "sirket")

    if config.RUN_ONCE:
        run_cycle(state)
        return

    try:
        while True:
            run_cycle(state)
            time.sleep(config.LOOP_SLEEP_SECONDS)
    except KeyboardInterrupt:
        print("Bot durduruldu (Ctrl+C).")


if __name__ == "__main__":
    main()
