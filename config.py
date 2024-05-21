import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

CERTIFICATE_PATH = os.getenv("CERTIFICATE_PATH")
URL_TOKEN = os.getenv("URL_TOKEN")
URL_CHAT = os.getenv("URL_CHAT")
AUTHORIZATION_HEADER = os.getenv("AUTHORIZATION_HEADER")
SCOPE = os.getenv("SCOPE")
CONTENT_TYPE_FORM = 'application/x-www-form-urlencoded'
CONTENT_TYPE_JSON = 'application/json'
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
