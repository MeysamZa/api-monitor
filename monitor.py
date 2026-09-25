import os
import requests
from datetime import datetime



# ==========================================
# Configuration
# ==========================================

HIGH_BTC_ETH_RATIO = 31.5
LOW_BTC_ETH_RATIO = 31

NOBITEX_API = "https://apiv2.nobitex.ir/market/stats"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

COMMAND = os.environ.get("COMMAND", "")
COMMAND_CHAT_ID = os.environ.get("COMMAND_CHAT_ID")


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

    response = requests.request("GET", NOBITEX_API, headers=headers, data=payload,params=params)

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

def send_telegram(message, chat_id=None):

    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message
        },
        timeout=15
    )

    response.raise_for_status()


def handle_command(command, chat_id, btc, eth):

    command = command.strip().lower()

    if command == "/price":

        message = (
            "📊 Nobitex\n\n"
            f"₿ BTC/USDT: {btc:,.2f}\n"
            f"Ξ ETH/USDT: {eth:,.2f}\n"
            f"Ratio: {btc/eth:,.2f}\n\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        send_telegram(message, chat_id)
        return

    if command == "/help":

        message = (
            "🤖 دستورات ربات\n\n"
            "/price - قیمت BTC و ETH\n"
            "/status - وضعیت آخرین محاسبه\n"
            "/signal - بررسی سیگنال\n"
            "/help - راهنمای دستورات"
        )

        send_telegram(message, chat_id)
        return

    send_telegram(
        f"❓ دستور ناشناخته:\n{command}\n\n"
        "برای مشاهده دستورات /help را بفرستید.",
        chat_id
    )

# ==========================================
# Your conditions
# ==========================================

def check_conditions(btc, eth):

    import json
    from pathlib import Path

    state_file = Path("last_result.json")

    # ==========================================
    # خواندن نتیجه اجرای قبلی
    # ==========================================

    previous_result = None

    if state_file.exists():

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                previous_result = json.load(f)

        except Exception as e:
            print(f"Could not read previous result: {e}")


    # ==========================================
    # استفاده از نتیجه قبلی
    # ==========================================

    if previous_result:

        previous_btc = previous_result.get("btc")
        previous_eth = previous_result.get("eth")
        previous_ratio = previous_result.get("ratio")

        print(f"Previous Data: {previous_result}")

    # ==========================================
    # محاسبات فعلی
    # ==========================================
    
    current_ratio = btc / eth
    current_result = {
        "btc": btc,
        "eth": eth,
        "ratio": current_ratio,
    }
    print(f"Current Data: {current_result}")


        # ======================================
        # شروط خودت را اینجا بنویس
        # ======================================

        # مثال:
        #
        # if btc > previous_btc:
        #     ...
        #
        # if previous_result.get("signal") == "BUY":
        #     ...


    # ==========================================
    # ذخیره نتیجه فعلی
    # ==========================================

    with open(state_file, "w", encoding="utf-8") as f:

        json.dump(
            current_result,
            f,
            ensure_ascii=False,
            indent=2
        )


    # ==========================================
    # شرط ارسال Telegram
    # ==========================================

    condition = False
    
    if current_ratio>=HIGH_BTC_ETH_RATIO:
        condition = True
        signal="Chnage BTC to ETH"
        
    if current_ratio<=LOW_BTC_ETH_RATIO:
        condition = True
        signal="Chnage ETH to BTC"
    

    if condition:

        return (
            "🚨 Nobitex Alert\n\n"
            f"BTC/USDT: {btc:,.2f}\n"
            f"ETH/USDT: {eth:,.2f}\n"
            f"Ratio: {current_ratio:,.2f}\n"
            f"Signal: {signal}\n"
        )

    return None

# ==========================================
# Main
# ==========================================

def main():

    btc, eth = get_prices()
    print(f"BTC/USDT = {btc:,.2f}")
    print(f"ETH/USDT = {eth:,.2f}")

    # اگر Workflow از Telegram فراخوانی شده
    if COMMAND:

        print(f"Telegram command: {COMMAND}")

        handle_command(
            COMMAND,
            COMMAND_CHAT_ID,
            btc,
            eth
        )

        return

    # در غیر این صورت، اجرای عادی مانیتور

    message = check_conditions(btc, eth)

    if message:
        print("Condition matched. Sending Telegram...")
        send_telegram(message)
    else:
        print("No condition matched. Nothing will be sent.")


if __name__ == "__main__":
    main()
