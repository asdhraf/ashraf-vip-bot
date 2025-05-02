

def analyze_stock(symbol, now):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="7d", interval="1d", prepost=True)
        
        print(f"\n🔍 تحليل {symbol}:")
        print(hist.tail(2))  # طباعة آخر يومين من البيانات
        
        if hist.empty or len(hist) < 2:
            print(f"⚠️ لا توجد بيانات كافية لـ {symbol}")
            return

        last_close = hist.iloc[-2]['Close']
        current_price = hist.iloc[-1]['Close']
        volume = hist.iloc[-1]['Volume']
        prev_high = hist['High'].iloc[:-1].max()
        
        print(f"💰 السعر الحالي: {current_price}, الحجم: {volume}, الأعلى السابق: {prev_high}")
        
        if current_price < PRICE_LIMIT and current_price > prev_high and volume > 500000:
            # ---- حساب الأهداف والوقف ----
            stop_loss = round(current_price * 0.93, 2)
            target1 = round(current_price * 1.07, 2)
            target2 = round(current_price * 1.15, 2)
            
            # ---- بناء الرسالة ----
            message = f"""📈 <b>إشارة تداول: {symbol}</b>
⏰ الوقت: {now}
💵 السعر الحالي: {current_price:.2f}
🛑 وقف الخسارة: {stop_loss}
🎯 الهدف الأول: {target1}
🎯 الهدف الثاني: {target2}"""
            
            # ---- إرسال الرسالة ----
            send_to_telegram(message)
            time.sleep(1)  # تأخير بين الإشعارات
            
    except Exception as e:
        print(f"❌ خطأ في {symbol}: {str(e)}")



