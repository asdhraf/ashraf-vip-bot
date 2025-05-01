
import yfinance as yf
import requests
import datetime
import pytz
import csv
import time
import threading
from flask import Flask
import os

# ----- إعدادات البوت (يجب تعيينها عبر متغيرات البيئة) -----
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # ⚠️ احذف التوكن الافتراضي!
CHAT_ID = os.environ.get('CHAT_ID')      # ⚠️ تأكد من الـ Chat ID
PRICE_LIMIT = 10.0

# ----- التوقيت الزمني -----
riyadh = pytz.timezone('Asia/Riyadh')

# ----- إعدادات السيرفر -----
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت يعمل بشكل طبيعي"

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

# ----- دالة إرسال الرسائل مع توثيق كامل -----
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=payload)
        print(f"\n📊 حالة الإرسال: {response.status_code}")
        print(f"📄 تفاصيل الرد: {response.text}")
        
        if response.status_code == 200:
            print("✔️ تم الإرسال بنجاح إلى التليجرام")
            return True
        else:
            print(f"❌ فشل الإرسال: {response.text}")
            return False
    except Exception as e:
        print(f"🔥 خطأ شبكي حادث: {e}")
        return False

# ----- اختبار البوت قبل البدء -----
def test_telegram_bot():
    print("\n🔍 جاري اختبار إعدادات البوت...")
    test_message = "🔔 <b>اختبار تشغيل البوت</b>\n" \
                   "إذا رأيت هذه الرسالة، فالإعدادات صحيحة ✅"
    
    if send_to_telegram(test_message):
        print("\n🎉 تم التحقق من صحة البوت بنجاح!")
        return True
    else:
        print("\n❌ فشل الاختبار: الرجاء فحص التوكن ورقم القناة.")
        return False

# ----- تحليل الأسهم -----
def analyze_stock(symbol, now):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="7d", interval="1d", prepost=True)
        
        if hist.empty or len(hist) < 2:
            return

        last_close = hist.iloc[-2]['Close']
        current_price = hist.iloc[-1]['Close']
        volume = hist.iloc[-1]['Volume']
        prev_high = hist['High'][:-1].max()

        if current_price < PRICE_LIMIT and current_price > prev_high and volume > 500000:
            stop_loss = round(current_price * 0.93, 2)
            target1 = round(current_price * 1.07, 2)
            target2 = round(current_price * 1.15, 2)
            message = f"""📈 <b>إشارة تداول: {symbol}</b>
⏰ الوقت: {now}
💵 السعر الحالي: {current_price:.2f}
🛑 وقف الخسارة: {stop_loss}
🎯 الهدف الأول: {target1}
🎯 الهدف الثاني: {target2}"""
            send_to_telegram(message)
            time.sleep(1)  # تأخير بين الإشعارات

    except Exception as e:
        print(f"⚠️ خطأ في تحليل {symbol}: {e}")

# ----- فحص جميع الأسهم -----
def run_analysis():
    try:
        if not os.path.exists("all_us_tickers.csv"):
            print("❌ ملف الأسهم غير موجود!")
            return

        with open("all_us_tickers.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            now = datetime.datetime.now(riyadh).strftime('%Y-%m-%d %H:%M:%S')
            for row in reader:
                symbol = row.get('Symbol')
                if symbol:
                    analyze_stock(symbol, now)
                    time.sleep(2)  # تأخير 2 ثواني بين الطلبات
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")

# ----- إرسال إشعار التشغيل -----
def send_alive_message():
    while True:
        send_to_telegram("🔄 البوت يعمل بدون أخطاء")
        time.sleep(60 * 60 * 12)  # كل 12 ساعة

# ----- التشغيل الرئيسي -----
def main():
    if test_telegram_bot():
        send_to_telegram("🚀 البوت يعمل الآن!")
        while True:
            run_analysis()
            time.sleep(300)  # إعادة التحليل كل 5 دقائق
    else:
        print("⛔ تم إيقاف السكربت بسبب أخطاء الإعدادات.")

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=send_alive_message, daemon=True).start()
    main()



