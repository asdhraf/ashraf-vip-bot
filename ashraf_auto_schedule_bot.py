import yfinance as yf
import requests
import datetime
import pytz
import csv
import time
import threading
from flask import Flask
import os

# إعدادات البوت
BOT_TOKEN = '7698515759:AAGJzxXN4t5yPUzSHHr4nv4xSzqUM5E1FHs'
CHAT_ID = '@ashraf_1m_bot'
PRICE_LIMIT = 10.0

# توقيت الرياض
riyadh = pytz.timezone('Asia/Riyadh')

# إنشاء سيرفر وهمي لتجاوز Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Ashraf Bot is running!"

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

# إرسال رسالة تيليجرام
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ خطأ أثناء الإرسال: {e}")

# حساب RSI
def calculate_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.isna().iloc[-1] else None

# حساب إشارة MACD
def calculate_macd_signal(close_prices):
    exp1 = close_prices.ewm(span=12, adjust=False).mean()
    exp2 = close_prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    if macd.iloc[-1] > signal.iloc[-1]:
        return "bullish"
    else:
        return "bearish"

# تحليل سهم مفرد
def analyze_stock(symbol, now):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="7d", interval="1d")

        if hist.empty or len(hist) < 2:
            return

        last_close = hist['Close'][-2]
        current_price = hist['Close'][-1]
        volume = hist['Volume'][-1]
        prev_high = hist['High'][:-1].max()

        if current_price < PRICE_LIMIT and current_price > prev_high and volume > 500000:
            rsi = calculate_rsi(hist['Close'])
            macd_signal = calculate_macd_signal(hist['Close'])

            if rsi and (30 < rsi < 70) and macd_signal == "bullish":
                stop_loss = round(current_price * 0.93, 2)
                target1 = round(current_price * 1.07, 2)
                target2 = round(current_price * 1.15, 2)
                message = f"""📈 <b>فرصة ممتازة: {symbol}</b>
⏰ وقت الدخول: {now}
💵 سعر الدخول: {current_price:.2f}
🛑 وقف الخسارة: {stop_loss}
🎯 الهدف الأول: {target1}
🎯 الهدف الثاني: {target2}
📊 RSI: {rsi:.2f}
📌 القرار: دخول"""
                send_to_telegram(message)

    except Exception as e:
        print(f"❌ خطأ أثناء تحليل {symbol}: {e}")

# تحليل كل الأسهم
def run_analysis():
    try:
        with open("all_us_tickers.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            now = datetime.datetime.now(riyadh).strftime('%Y-%m-%d %H:%M:%S')
            for row in reader:
                symbol = row['Symbol']
                try:
                    analyze_stock(symbol, now)
                    time.sleep(2.5)  # ✅ لتفادي الحظر من Yahoo
                except Exception as e:
                    if "Too Many Requests" in str(e):
                        print("⏸ تم الحظر مؤقتًا. انتظر 60 ثانية...")
                        time.sleep(60)
                    else:
                        print(f"❌ خطأ أثناء تحليل {symbol}: {e}")
    except Exception as e:
        print(f"❌ خطأ عام في فتح الملف: {e}")

# رسالة كل 12 ساعة
def send_alive_message():
    while True:
        send_to_telegram("✅ البوت شغال بشكل طبيعي!")
        time.sleep(60 * 60 * 12)

# التشغيل
def main():
    while True:
        run_analysis()
        time.sleep(300)  # كل 5 دقائق

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    threading.Thread(target=send_alive_message).start()
    main()
