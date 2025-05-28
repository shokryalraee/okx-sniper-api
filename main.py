from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# تحليل الشموع المغلقة
def analyze_candles(candles):
    ob_zones = []
    fvg_zones = []
    bos_points = []

    # ترتيب الشموع من الأقدم إلى الأحدث
    candles = list(reversed(candles))

    for i in range(2, len(candles)):
        _, o, h, l, c, _, _ = candles[i]
        o = float(o)
        h = float(h)
        l = float(l)
        c = float(c)

        prev1 = list(map(float, candles[i-1][1:5]))
        prev2 = list(map(float, candles[i-2][1:5]))

        # Bearish OB
        if prev1[3] < l and prev1[0] < prev1[3] and c < o:
            ob_zones.append({
                "type": "bearish",
                "start": prev1[1],
                "end": prev1[2],
                "index": i-1
            })

        # FVG
        if prev2[2] > prev1[1] and l > prev2[2]:
            fvg_zones.append({
                "gap_start": prev2[2],
                "gap_end": l,
                "index": i
            })

        # BOS
        if c > prev1[1] and c > prev2[1]:
            bos_points.append({
                "type": "bullish",
                "close": c,
                "index": i
            })

    return ob_zones, fvg_zones, bos_points

# Endpoint للتحليل
@app.route("/analyze", methods=["GET"])
def analyze():
    symbol = request.args.get("symbol", "BTC-USDT")
    bar = request.args.get("timeframe", "4H")

    # جلب الشموع من OKX
    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={bar}&limit=100"
    r = requests.get(url)
    data = r.json()
    candles = data.get("data", [])

    if not candles:
        return jsonify({"error": "لا توجد بيانات شموع"})

    ob, fvg, bos = analyze_candles(candles)

    return jsonify({
        "symbol": symbol,
        "timeframe": bar,
        "order_blocks": ob,
        "fvg": fvg,
        "bos": bos
    })

# الصفحة الرئيسية
@app.route("/")
def home():
    return "✅ API شغال تمام"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
