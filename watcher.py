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

ANDROID KULLANIMI: Telefonun bilgisayar gibi Python calistiramadigi icin
bu script iki modda calisabilir (config.py > RUN_ONCE ile secilir):
  - RUN_ONCE=true  (varsayilan): GitHub Actions gibi bir bulut ortaminda
    saatte bir tetiklenir, kontrol eder, Telegram'a bildirim atar, cikar.
    Telefonun hicbir sey calistirmasina gerek yok, sadece Telegram bildirimi
    alirsin. Kurulum adimlari README.md'de.
  - RUN_ONCE=false: Termux uygulamasiyla telefonun uzerinde surekli
    calistirmak istersen (sinirli/pilli kullanim icin).

Kar garantisi YOKTUR. Trend takip stratejileri yatay piyasalarda ust
uste yanlis sinyal verebilir. Sinyalleri kendi gozlemlerinle
karsilastirmadan uygulama.
"""

import csv
import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import config
import notifier
import position_sizer
import strategy

TR_TZ = ZoneInfo("Europe/Istanbul")


def load_state():
    if os.path.isfile(config.STATE_FILE):
        with open(config.STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(config.STATE_FILE, "w") as f:
        json.dump(state, f, default=str)


def log_signal(row):
    file_exists = os.path.isfile(config.SIGNAL_LOG_FILE)
    with open(config.SIGNAL_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["zaman", "sembol", "yon", "fiyat", "sl", "tp", "onerilen_adet"])
        writer.writerow(row)


def is_market_open():
    now = datetime.now(TR_TZ)
    if now.weekday() >= 5:  # 5=Cumartesi, 6=Pazar
        return False
    current = now.strftime("%H:%M")
    return "10:00" <= current <= "18:10"


def process_symbol(symbol, state):
    daily_trend = strategy.get_daily_trend(symbol)
    signal, candle_time = strategy.get_entry_signal(symbol, daily_trend)
    if signal is None:
        return

    candle_key = str(candle_time)
    if state.get(symbol) == candle_key:
        return  # bu mum icin zaten sinyal verildi, tekrar uyarma

    atr_value = strategy.get_atr_value(symbol)
    price = strategy.get_last_price(symbol)
    if not atr_value or not price:
        return

    sl_price = price - (atr_value * config.ATR_SL_MULT)
    tp_price = price + (atr_value * config.ATR_TP_MULT)

    shares = position_sizer.suggest_shares(price, sl_price)

    message = (
        f"[{symbol}] {signal} sinyali\n"
        f"Fiyat: {price:.2f} TL\n"
        f"Stop: {sl_price:.2f} TL | Hedef: {tp_price:.2f} TL\n"
        f"Onerilen adet (bilgi amacli, {config.BUDGET_TRY:.0f} TL butceye gore): {shares}"
    )
    print(message)
    log_signal([datetime.now(), symbol, signal, round(price, 2),
                round(sl_price, 2), round(tp_price, 2), shares])
    notifier.send(message)

    state[symbol] = candle_key


def run_cycle(state):
    if is_market_open():
        for symbol in config.WATCHLIST:
            try:
                process_symbol(symbol, state)
            except Exception as exc:
                print(f"[{symbol}] Hata: {exc}")
        save_state(state)
    else:
        print("Piyasa kapali.")


def main():
    state = load_state()
    print("BIST Sinyal Botu baslatildi.")
    print("Takip listesi:", ", ".join(config.WATCHLIST))

    if config.RUN_ONCE:
        # GitHub Actions gibi zamanlanmis/bulut ortamlari icin: bir kere
        # kontrol eder ve cikar - zamanlamayi cron yapar.
        run_cycle(state)
        return

    # Termux gibi surekli acik kalan ortamlar icin: sonsuz dongu.
    try:
        while True:
            run_cycle(state)
            time.sleep(config.LOOP_SLEEP_SECONDS)
    except KeyboardInterrupt:
        print("Bot durduruldu (Ctrl+C).")


if __name__ == "__main__":
    main()
