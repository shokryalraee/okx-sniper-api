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
    return "صاعد" if df['ema20'].iloc[-1] > df['ema50'].iloc[-1] else "هابط"

# ✅ استخراج Order Blocks
def find_ob(df):
    ob_list = []
    for i in range(3, len(df)-3):
        body = abs(df['close'][i] - df['open'][i])
        full_range = df['high'][i] - df['low'][i]
        if body > full_range * 0.6:
            is_bull = df['close'][i] > df['open'][i]
            bos = df['high'][i+1] > df['high'][i] if is_bull else df['low'][i+1] < df['low'][i]
            if bos:
                ob_list.append({
                    "type": "demand" if is_bull else "supply",
                    "entry": df['open'][i],
                    "zone_low": df['low'][i],
                    "zone_high": df['high'][i],
                    "timestamp": df['timestamp'][i]
                })
    return ob_list

# ✅ توليد التقرير
def generate_report(df, ob_list, trend):
    last_price = df['close'].iloc[-1]
    ob = next((ob for ob in reversed(ob_list) if ob['type'] == ('demand' if trend == "صاعد" else 'supply')), None)

    if not ob:
        return "🚫 لا توجد منطقة مناسبة حسب الاتجاه."

    sl = ob['zone_low'] if trend == "صاعد" else ob['zone_high']
    tp1 = last_price + (last_price - sl) * 1.5 if trend == "صاعد" else last_price - (sl - last_price) * 1.5
    tp2 = last_price + (last_price - sl) * 2.5 if trend == "صاعد" else last_price - (sl - last_price) * 2.5

    report = f"""
🔸 العملة: BTC/USDT
السعر اللحظي: ${last_price}
نوع الصفقة: {"LONG" if trend == "صاعد" else "SHORT"}

التحليل الفني:
- الاتجاه العام: {trend}
- منطقة OB: {ob['zone_low']} → {ob['zone_high']}
- نقطة الدخول: {ob['entry']}
- SL: {sl}
- TP1: {tp1:.2f} / TP2: {tp2:.2f}
- RR: 1:{round((tp1-last_price)/(last_price-sl),2)}
✅ تم توليد التقرير بنجاح!
"""
    return report

# ✅ إرسال إلى Telegram
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    res = requests.post(url, data=payload)
    return res

# ✅ تشغيل كل شيء
if __name__ == "__main__":
    df = fetch_okx_data()
    trend = detect_trend(df)
    ob_list = find_ob(df)
    result = generate_report(df, ob_list, trend)
    print(result)

    # 📤 إرسال إلى تليجرام
    TELEGRAM_BOT_TOKEN = "7716957577:AAH3lAqHFh-wsg8DMJASAaEg6GyQDAopmPU"
    TELEGRAM_CHAT_ID = "1056165559"
    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, result)
