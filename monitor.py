import os
import requests


# ==========================================
# Configuration
# ==========================================

NOBITEX_API = "https://apiv2.nobitex.ir/market/stats"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


# ==========================================
# Get current prices
# ==========================================

def get_prices():

    payload = {}
    headers = {
    'Accept': 'application/json'
  }
    params = {
        "srcCurrency": "btc,eth",
        "dstCurrency": "usdt"
    }

    response = requests.get(
        NOBITEX_API,
        data=payload,
        headers=headers
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise Exception(f"Nobitex API error: {data}")

    btc_price = float(data["stats"]["btc-usdt"]["latest"])
    eth_price = float(data["stats"]["eth-usdt"]["latest"])

    return btc_price, eth_price


# ==========================================
# Send Telegram message
# ==========================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=15
    )

    response.raise_for_status()


# ==========================================
# Your conditions
# ==========================================

def check_conditions(btc, eth):

    # ======================================
    # این قسمت را خودت تغییر بده
    # ======================================

    condition = False

    # مثال:
    #
    # condition = btc > 100000
    #
    # یا:
    #
    # condition = btc > 100000 and eth < 5000
    #
    # یا هر محاسبه دیگری که بخواهی

    if condition:

        message = (
            "🚨 Nobitex Alert\n\n"
            f"BTC/USDT: {btc:,.2f}\n"
            f"ETH/USDT: {eth:,.2f}"
        )

        return message

    return None


# ==========================================
# Main
# ==========================================

def main():

    btc, eth = get_prices()

    print(f"BTC/USDT = {btc:,.2f}")
    print(f"ETH/USDT = {eth:,.2f}")

    message = check_conditions(btc, eth)

    if message:
        print("Condition matched. Sending Telegram...")
        send_telegram(message)
    else:
        print("No condition matched. Nothing will be sent.")


if __name__ == "__main__":
    main()
