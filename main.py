import requests, os
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
CONTRACTS = ["LTC_USDT", "BROCCOLI_USDT", "ZEC_USDT", "MUBARAK_USDT"]
TIMEFRAMES = {"M15": "15m", "H1": "1h", "H4": "4h", "D1": "1d", "W1": "1w"}
THRESHOLD = 0.0015

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)

def get_candles(c, interval):
    try:
        url = f"https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract={c}&interval={interval}&limit=100"
        r = requests.get(url, timeout=10).json()
        r = r[::-1]
        closes = [float(x['c']) for x in r]
        highs = [float(x['h']) for x in r]
        lows = [float(x['l']) for x in r]
        return closes, highs, lows
    except: return None, None, None

def ema(prices, p):
    if len(prices) < p: return None
    k = 2/(p+1)
    e = sum(prices[:p])/p
    for price in prices[p:]: e = price*k + e*(1-k)
    return e

for CONTRACT in CONTRACTS:
    coin = CONTRACT.replace('_USDT','')
    for name, interval in TIMEFRAMES.items():
        closes, highs, lows = get_candles(CONTRACT, interval)
        if not closes: continue
        e34, e89 = ema(closes, 34), ema(closes, 89)
        cc, ch, cl = closes[-1], highs[-1], lows[-1]
        if e34 and (cl <= e34 <= ch or abs(cc-e34)/cc <= THRESHOLD):
            send(f"⚡️ *{coin} CHẠM EMA34 - {name}*\nGiá: `${cc}`\nEMA34: `${e34:.4f}`")
        if e89 and (cl <= e89 <= ch or abs(cc-e89)/cc <= THRESHOLD):
            send(f"🔥 *{coin} CHẠM EMA89 - {name}*\nGiá: `${cc}`\nEMA89: `${e89:.4f}`")
