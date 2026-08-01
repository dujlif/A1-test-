"""
notifier.py
OPSIYONEL Telegram bildirimi. Varsayilan kapali (config.USE_TELEGRAM = False).

Telefonuna anlik sinyal bildirimi almak icin:
  1. Telegram'da @BotFather ile konusup yeni bir bot olustur, sana bir
     TOKEN verecek.
  2. Olusturdugun botla bir kere mesajlas (herhangi bir sey yaz),
     sonra @userinfobot ile kendi chat_id'ni ogren.
  3. config.py icinde TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID alanlarini
     doldur, USE_TELEGRAM = True yap.
"""

import requests

import config


def send(message):
    if not config.USE_TELEGRAM or not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(
            url,
            data={"chat_id": config.TELEGRAM_CHAT_ID, "text": message},
            timeout=5,
        )
    except Exception as exc:
        print(f"[notifier] Telegram mesaji gonderilemedi: {exc}")
