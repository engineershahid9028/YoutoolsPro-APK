import os, time, hmac, hashlib, requests

BINANCE_API = "https://api.binance.com"
API_KEY = os.getenv("BINANCE_API_KEY")
SECRET = os.getenv("BINANCE_SECRET_KEY")


def verify_usdt_payment(tx_hash, min_amount=5):
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = hmac.new(
        SECRET.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-MBX-APIKEY": API_KEY
    }

    url = f"{BINANCE_API}/sapi/v1/capital/deposit/hisrec?{query}&signature={signature}"

    res = requests.get(url, headers=headers, timeout=10)

    if res.status_code != 200:
        return False

    deposits = res.json()

    for tx in deposits:
        if (
            tx["txId"] == tx_hash and
            tx["coin"] == "USDT" and
            tx["network"] in ["TRX", "TRC20"] and
            float(tx["amount"]) >= min_amount and
            tx["status"] == 1
        ):
            return True

    return False