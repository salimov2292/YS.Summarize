import requests
from telegram.ext import ApplicationBuilder, CommandHandler
from config import TELEGRAM_BOT_TOKEN
from auth import get_access_token
from chat import make_chat_request, print_chat_response
from handlers import start, summarize

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
