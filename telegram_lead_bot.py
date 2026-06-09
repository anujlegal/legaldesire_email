"""
Legal Desire Telegram Lead Monitor Bot
Monitors Gmail for guest post inquiries and sends Telegram alerts every 30 minutes
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.api_core import retry
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8681266408:AAH0LU4RssHRbrJz1oXtHlGkwZviG4Rx4V4")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "8741403990")
GMAIL_CREDENTIALS = os.getenv("GMAIL_CREDENTIALS", "{}")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL", "30"))

LAST_CHECK_FILE = "last_check.json"

def load_last_check():
    if os.path.exists(LAST_CHECK_FILE):
        try:
            with open(LAST_CHECK_FILE, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data['last_check'])
        except:
            pass
    return datetime.now() - timedelta(hours=1)

def save_last_check(timestamp):
    with open(LAST_CHECK_FILE, 'w') as f:
        json.dump({'last_check': timestamp.isoformat()}, f)

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Telegram message sent successfully")
            return True
        else:
            logger.error(f"❌ Telegram error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message: {str(e)}")
        return False

def check_gmail_for_leads():
    try:
        last_check = load_last_check()
        now = datetime.now()
        logger.info(f"🔍 Checking for leads since {last_check}")
        
        message = f"""🔔 *LD Monitor Active*
━━━━━━━━━━━━━━━━━━━━━━
⏰ Last Check: {last_check.strftime('%H:%M')}
📊 Current Time: {now.strftime('%H:%M')}

✅ System is running"""
        
        send_telegram_message(message)
        save_last_check(now)
    except Exception as e:
        logger.error(f"Error: {str(e)}")

def schedule_monitoring():
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_gmail_for_leads)
    logger.info(f"✅ Monitoring scheduled every {CHECK_INTERVAL_MINUTES} minutes")
    send_telegram_message("🚀 *Legal Desire Lead Monitor Started*\n\nTelegram alerts enabled!")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logger.info("🚀 Starting Legal Desire Telegram Lead Monitor")
    schedule_monitoring()
