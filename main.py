import pandas as pd
import numpy as np
import requests
from ta import add_all_ta_features

# ✅ جلب بيانات OKX - 1000 شمعة 1H
def fetch_okx_data(symbol="BTC-USDT", interval="1H", limit=1000):
    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()['data']
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close',
        'volume_token', 'volume_usdt', 'volume_alt', 'unknown'])
    df = df.iloc[::-1].reset_index(drop=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(np.int64), unit='ms')
    for col in ['open', 'high', 'low', 'close', 'volume_token']:
        df[col] = pd.to_numeric(df[col])
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume_token']]

# ✅ تحليل الاتجاه العام
def detect_trend(df):
    df['ema20'] = df['close'].rolling(20).mean()
    df['ema50'] = df['close'].rolling(50).mean()
    trend = "صاعد" if df['ema20'].iloc[-1] > df['ema50'].iloc[-1] else "هابط"
    return trend
import requests

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response

# 🔧 استخدم هنا توكن البوت و Chat ID
TELEGRAM_BOT_TOKEN = "🔑 ضع التوكن هنا بين علامتي تنصيص"
TELEGRAM_CHAT_ID = "💬 ضع الشات آي دي هنا"

# 📤 أرسل التقرير لتليجرام
send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, result)
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    res = requests.post(url, data=payload)
    return res

# 🔐 بيانات البوت
TELEGRAM_BOT_TOKEN = "🔑 ضع التوكن هنا"
TELEGRAM_CHAT_ID = "💬 ضع الشات ID هنا كرقم"

# 📤 أرسل التقرير
send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, result)
