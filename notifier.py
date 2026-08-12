"""
notifier.py
Telegram bildirimi. config.py > TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
dolu degilse (ornegin yerel testte) sessizce atlar.
"""

import requests

import config


def send(message):
    if not config.USE_TELEGRAM:
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
