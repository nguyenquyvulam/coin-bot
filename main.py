import requests, os

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
CONTRACTS = ["LTC_USDT", "BROCCOLI_USDT", "ZEC_USDT", "MUBARAK_USDT"]
TIMEFRAMES = {"M15": "15m", "H1": "1h", "H4": "4h", "D1": "1d", "W1": "1w"}
TOUCH_THRESHOLD = 0.0015

def gui_tele(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def get_candles(c, interval):
    url = f"https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract={c}&interval={interval}&limit=100"
    try:
        r = requests.get(url, timeout=10).json()
        r = r[::-1]
        return [float(x['c']) for x in r], [float(x['h']) for x in r], [float(x['l']) for x in r]
    except: return None, None, None

def calc_ema(prices, period):
    if len(prices) < period: return None
    k = 2/(period+1)
    ema = sum(prices[:period])/period
    for p in prices[period:]: ema = p*k + ema*(1-k)
    return ema

for CONTRACT in CONTRACTS:
    coin = CONTRACT.replace('_USDT','')
    for tf_name, tf_interval in TIMEFRAMES.items():
        closes, highs, lows = get_candles(CONTRACT, tf_interval)
        if not closes: continue
        ema34 = calc_ema(closes, 34)
        ema89 = calc_ema(closes, 89)
        cc, ch, cl = closes[-1], highs[-1], lows[-1]
        if ema34 and (cl <= ema34 <= ch or abs(cc-ema34)/cc <= TOUCH_THRESHOLD):
            gui_tele(f"⚡️ *{coin} CHẠM EMA34 - {tf_name}*\nGiá: `${cc}`\nEMA34: `${ema34:.4f}`")
        if ema89 and (cl <= ema89 <= ch or abs(cc-ema89)/cc <= TOUCH_THRESHOLD):
            gui_tele(f"🔥 *{coin} CHẠM EMA89 - {tf_name}*\nGiá: `${cc}`\nEMA89: `${ema89:.4f}`")
