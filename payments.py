import requests, hmac, hashlib, time, os

BINANCE_API = "https://api.binance.com"
API_KEY = os.getenv("BINANCE_API_KEY")
SECRET = os.getenv("BINANCE_SECRET_KEY")

def verify_payment(tx_hash, expected_amount):
    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = hmac.new(SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

    headers = {"X-MBX-APIKEY": API_KEY}
    url = f"{BINANCE_API}/sapi/v1/capital/deposit/hisrec?{query}&signature={signature}"

    res = requests.get(url, headers=headers).json()

    for tx in res:
        if tx["txId"] == tx_hash and float(tx["amount"]) >= expected_amount:
            return True

    return False
