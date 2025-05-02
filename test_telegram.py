import requests

BOT_TOKEN = '7698515759:AAGJzxXN4t5yPUzSHHr4nv4xSzqUM5E1FHs'
CHAT_ID = '@ashraf_1m_bot'  # أو ID القناة إذا كانت خاصة

message = "✅ تجربة إرسال من Koyeb!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': CHAT_ID,
    'text': message,
    'parse_mode': 'HTML'
}

response = requests.post(url, data=payload)
print(response.text)
