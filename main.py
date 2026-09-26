import requests
import time

# --- ĐÃ ĐIỀN SẴN CHO BẠN ---
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

CONTRACTS = ["LTC_USDT", "BROCCOLI_USDT", "ZEC_USDT", "MUBARAK_USDT"]
TIMEFRAMES = {"M15": "15m", "H1": "1h", "H4": "4h", "D1": "1d", "W1": "1w"}
TOUCH_THRESHOLD = 0.0015

def gui_tele(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_candles(contract, interval, limit=100):
    url = f"https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract={contract}&interval={interval}&limit={limit}"
    try:
        r = requests.get(url, timeout=10).json()
        if not r or isinstance(r, dict): return None, None, None
        r = r[::-1]
        closes = [float(x['c']) for x in r]
        highs = [float(x['h']) for x in r]
        lows = [float(x['l']) for x in r]
        return closes, highs, lows
    except: return None, None, None

def calc_ema(prices, period):
    if len(prices) < period: return [None]*len(prices)
    k = 2 / (period + 1)
    sma = sum(prices[:period]) / period
    ema = [sma]
    for price in prices[period:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return [None]*(len(prices)-len(ema)) + ema

def check_touch(close, high, low, ema_val):
    if ema_val is None: return False
    if low <= ema_val <= high: return True
    if abs(close - ema_val) / close <= TOUCH_THRESHOLD: return True
    return False

gui_tele(f"✅ *Bot Gate đã ONLINE*\nCoin: LTC, BROCCOLI, ZEC, MUBARAK\nKhung: M15, H1, H4, D1, W1\nNgưỡng: 0.15%")

last_alert = {}
while True:
    for CONTRACT in CONTRACTS:
        coin_name = CONTRACT.replace('_USDT','')
        for tf_name, tf_interval in TIMEFRAMES.items():
            closes, highs, lows = get_candles(CONTRACT, tf_interval)
            if not closes: continue
            ema34 = calc_ema(closes, 34)
            ema89 = calc_ema(closes, 89)
            curr_close, curr_high, curr_low = closes[-1], highs[-1], lows[-1]
            c34, c89 = ema34[-1], ema89[-1]
            if check_touch(curr_close, curr_high, curr_low, c34):
                key = f"{CONTRACT}_{tf_name}_34"
                if time.time() - last_alert.get(key, 0) > 1800:
                    gui_tele(f"⚡️ *{coin_name} CHẠM EMA34 - {tf_name}*\nGiá: `${curr_close}`\nEMA34: `${c34:.4f}`")
                    last_alert[key] = time.time()
            if check_touch(curr_close, curr_high, curr_low, c89):
                key = f"{CONTRACT}_{tf_name}_89"
                if time.time() - last_alert.get(key, 0) > 1800:
                    gui_tele(f"🔥 *{coin_name} CHẠM EMA89 - {tf_name}*\nGiá: `${curr_close}`\nEMA89: `${c89:.4f}`")
                    last_alert[key] = time.time()
            time.sleep(0.5)
    time.sleep(120)
