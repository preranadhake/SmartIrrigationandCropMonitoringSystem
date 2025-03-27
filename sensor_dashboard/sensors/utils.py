import requests
from django.conf import settings

def send_telegram_message(message):
   
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",  
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error while sending Telegram message: {e}")
        return False
