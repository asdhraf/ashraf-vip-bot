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
CHAT_ID = '@aashraf_vip'  # تأكد أنها القناة الصحيحة
PRICE_LIMIT = 10.0

# توقيت الرياض
riyadh = pytz.timezone('Asia/Riyadh')

# سيرفر وهمي
app = Flask(__name__)
@app.route('/')
def home():
    return "Ashraf Bot is running!"

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

# إرسال رسالة للتيليجرام
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("❌ فشل الإرسال:", response.text)
    except Exception as e:
        print(f"❌ خطأ أثناء الإرسال: {e}")

# تحليل السهم
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
            stop_loss = round(current_price * 0.93, 2)
            target1 = round(current_price * 1.07, 2)
            target2 = round(current_price * 1.15, 2)
            message = f"""📈 <b>فرصة ممتازة: {symbol}</b>
⏰ وقت الدخول: {now}
💵 سعر الدخول: {current_price:.2f}
🛑 وقف الخسارة: {stop_loss}
🎯 الهدف الأول: {target1}
🎯 الهدف الثاني: {target2}
📌 القرار: دخول"""
            send_to_telegram(message)
            time.sleep(1)  # تأخير بسيط بين كل سهم لتجنب الحظر

    except Exception as e:
        print(f"❌ خطأ أثناء تحليل السهم {symbol}: {e}")

# فحص كل الأسهم
def run_analysis():
    try:
        with open("all_us_tickers.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            now = datetime.datetime.now(riyadh).strftime('%Y-%m-%d %H:%M:%S')
            for row in reader:
                symbol = row['Symbol']
                analyze_stock(symbol, now)
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

# إرسال رسالة "البوت شغال"
def send_alive_message():
    while True:
        send_to_telegram("✅ البوت شغال بشكل طبيعي")
        time.sleep(60 * 60 * 12)

# رسالة اختبار مبدئية
def send_test_message():
    send_to_telegram("✅ تم تشغيل البوت الآن - رسالة اختبار")

# تشغيل السكربت
def main():
    send_test_message()
    while True:
        run_analysis()
        time.sleep(300)

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    threading.Thread(target=send_alive_message).start()
    main()
