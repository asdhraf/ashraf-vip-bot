
import yfinance as yf
import requests
import datetime
import pytz
import csv
import time
import threading
from flask import Flask
import os

# ----- إعدادات البوت -----
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
PRICE_LIMIT = 10.0

riyadh = pytz.timezone('Asia/Riyadh')

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت يعمل!"

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

# ... (بقية الدوال كما هي)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=send_alive_message, daemon=True).start()
    main()



