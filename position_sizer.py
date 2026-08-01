"""
position_sizer.py
SADECE BILGI AMACLIDIR - otomatik emir GONDERMEZ.
Sinyal geldiginde, girdigin butce ve risk yuzdesine gore kac pay
alinabilecegini onerir. Nihai karar ve emir senin elinle verilir.
"""

import config


def suggest_shares(entry_price, stop_price):
    if not entry_price or not stop_price or entry_price <= 0:
        return 0

    stop_distance = abs(entry_price - stop_price)
    if stop_distance <= 0:
        return 0

    risk_amount = config.BUDGET_TRY * (config.RISK_PER_TRADE_PCT / 100.0)
    shares_by_risk = risk_amount / stop_distance
    shares_by_budget = config.BUDGET_TRY / entry_price

    shares = min(shares_by_risk, shares_by_budget)
    return max(int(shares), 0)
