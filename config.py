import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') 
TELEGRAM_CHANNEL = os.getenv('TELEGRAM_CHANNEL')
# INTERVAL = os.getenv('INTERVAL')
