import requests
import uuid
import json
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

# Загружаем переменные окружения из .env файла
load_dotenv()

# Константы
CERTIFICATE_PATH = os.getenv("CERTIFICATE_PATH")
URL_TOKEN = os.getenv("URL_TOKEN")
URL_CHAT = os.getenv("URL_CHAT")
AUTHORIZATION_HEADER = os.getenv("AUTHORIZATION_HEADER")
SCOPE = os.getenv("SCOPE")
CONTENT_TYPE_FORM = 'application/x-www-form-urlencoded'
CONTENT_TYPE_JSON = 'application/json'
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STICKER_FILE_ID = 'CAACAgIAAxkBAAEMJ6xmTFZnpp1E4c2smC_aJBobddxc4gACnlIAAg3eYEpmdLVnAS-J3jUE'  # Замените на ваш File ID стикера

def get_access_token():
    headers = {
        'Content-Type': CONTENT_TYPE_FORM,
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),  # Генерация уникального RqUID
        'Authorization': AUTHORIZATION_HEADER
    }
    response = requests.post(URL_TOKEN, headers=headers, data=SCOPE, verify=CERTIFICATE_PATH)
    response.raise_for_status()  # Проверка на ошибки
    token_data = response.json()
    return token_data.get('access_token')

def make_chat_request(access_token):
    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": "Сколько будет 2+2?"
            }
        ],
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1
    }
    
    headers = {
        'Content-Type': CONTENT_TYPE_JSON,
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(URL_CHAT, headers=headers, data=json.dumps(payload), verify=False)  # Отключаем проверку сертификата
    response.raise_for_status()  # Проверка на ошибки
    return response.json()

def print_chat_response(chat_data):
    choices = chat_data.get("choices", [])
    if choices and "message" in choices[0]:
        print(choices[0]["message"]["content"])
    else:
        print("Ответ не содержит поле 'content'")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Я готов к работе.')

async def summarize(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Я пока еще не готов, но буду мусолить вам глаза. Мучайте Каловрата! 💩')
    await update.message.reply_sticker(STICKER_FILE_ID)

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summarize", summarize))

    application.run_polling()

if __name__ == "__main__":
    try:
        access_token = get_access_token()
        if not access_token:
            print("Не удалось получить токен")
        else:
            chat_data = make_chat_request(access_token)
            print_chat_response(chat_data)
    except requests.RequestException as e:
        print(f"Произошла ошибка при выполнении запросов: {e}")

    main()
