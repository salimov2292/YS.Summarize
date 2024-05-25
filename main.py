import aiohttp
import uuid
import json
import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import ssl
from typing import List

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
STICKER_FILE_ID = 'CAACAgIAAxkBAAEMJ6xmTFZnpp1E4c2smC_aJBobddxc4gACnlIAAg3eYEpmdLVnAS-J3jUE'
CHAT_MODEL = "GigaChat"
TEMPERATURE = 1.0
TOP_P = 0.1
MAX_TOKENS = 512
REPETITION_PENALTY = 1.0

# Список для хранения последних сообщений
recent_messages: List[str] = []

# Создание SSLContext
def create_ssl_context(cert_path: str) -> ssl.SSLContext:
    ssl_context = ssl.create_default_context(cafile=cert_path)
    return ssl_context

# Обработка SSL сертификата
ssl_context = None
try:
    ssl_context = create_ssl_context(CERTIFICATE_PATH)
except Exception as e:
    logger.error(f'Ошибка при создании SSL контекста: {e}')

async def get_access_token() -> str:
    """Получение access token для аутентификации."""
    headers = {
        'Content-Type': CONTENT_TYPE_FORM,
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),  # Генерация уникального RqUID
        'Authorization': AUTHORIZATION_HEADER
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL_TOKEN, headers=headers, data=SCOPE, ssl=ssl_context) as response:
            response.raise_for_status()
            token_data = await response.json()
            return token_data.get('access_token')

async def make_chat_request(access_token: str, messages: List[str]) -> str:
    """Отправка запроса к GigaChat"""
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Ты — нейросеть, и твоя задача — суммировать сообщения из чата. Твоя цель — кратко и четко передать содержание общения, избегая лишней информации. Вот что нужно учитывать: упоминай пользователей по их никам, кратко передавай суть их сообщений, если один пользователь отвечает другому, упоминай это, упоминай использование стикеров, но не детализируй их содержание. Пример суммирования: Пользователь Alex написал, что планирует поездку на выходные. Пользователь Maria ответила пользователю Alex, что тоже хотела бы поехать. Пользователь John отправил стикер. Пользователь Lisa предложила встретиться в кафе. Используй этот формат для суммирования следующих сообщений из чата. Ты не имеешь своего мнения и критики. Ты просто суммируешь сообщения чата и все. И добавляй от себя любой эмодзи. Пример суммирования это пример, ты его никогда не пишешь! " + "\n".join(messages)
            }
        ],
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "n": 1,
        "stream": False,
        "max_tokens": MAX_TOKENS,
        "repetition_penalty": REPETITION_PENALTY
    }
    
    headers = {
        'Content-Type': CONTENT_TYPE_JSON,
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(URL_CHAT, headers=headers, data=json.dumps(payload), ssl=False) as response:
            response.raise_for_status()
            chat_data = await response.json()
            return chat_data.get("choices", [])[0].get("message", {}).get("content", "Ошибка суммирования")

def get_message_declension(number: int) -> str:
    """Правильное склонение слов: Сообщения, Сообщение, Сообщения."""
    if 11 <= number % 100 <= 14:
        return 'сообщений'
    last_digit = number % 10
    if last_digit == 1:
        return 'сообщение'
    elif 2 <= last_digit <= 4:
        return 'сообщения'
    else:
        return 'сообщений'

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text('Привет! Я готов к работе.')

async def summarize(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /summarize для суммирования последних сообщений."""
    if not recent_messages:
        await update.message.reply_text('Нет доступных сообщений для суммирования.')
        return

    num_messages = min(300, len(recent_messages))
    selected_messages = recent_messages[-num_messages:]  # Выбираем последние сообщения
    message_declension = get_message_declension(num_messages)

    logger.info("Последние сообщения для суммирования:")
    for message in selected_messages:
        logger.info(message)

    try:
        access_token = await get_access_token()
        summarized_text = await make_chat_request(access_token, selected_messages)
    except aiohttp.ClientError as e:
        logger.error(f'Ошибка при запросе: {e}')
        await update.message.reply_text(f'Произошла ошибка при суммировании сообщений: {e}')
        return

    await update.message.reply_text(f'Для суммирования я выбрал: {num_messages} {message_declension}')
    await update.message.reply_text(f'Суммированный текст: {summarized_text}')
    await update.message.reply_sticker(STICKER_FILE_ID)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений."""
    recent_messages.append(update.message.text)
    if len(recent_messages) > 300:
        recent_messages.pop(0)  # Удаляем самое старое сообщение, если больше 300

def main() -> None:
    """Основная функция для запуска бота."""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summarize", summarize))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info('Бот запущен и готов к работе.')
    application.run_polling()

if __name__ == "__main__":
    main()
