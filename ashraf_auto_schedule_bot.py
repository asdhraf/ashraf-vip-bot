def run_analysis():
    try:
        with open("all_us_tickers.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            now = datetime.datetime.now(riyadh).strftime('%Y-%m-%d %H:%M:%S')
            for row in reader:
                symbol = row['Symbol']
                try:
                    analyze_stock(symbol, now)
                    time.sleep(2.5)  # ✅ تأخير أطول لتفادي الحظر من Yahoo
                except Exception as e:
                    if "Too Many Requests" in str(e):
                        print("⏸ تم الحظر مؤقتًا. انتظر 60 ثانية...")
                        time.sleep(60)
                    else:
                        print(f"❌ خطأ أثناء تحليل {symbol}: {e}")
    except Exception as e:
        print(f"❌ خطأ عام في فتح الملف: {e}")
