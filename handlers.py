from telegram import Update
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Я готов к работе.')

async def summarize(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Я пока еще не готов, но буду мусолить вам глаза. Мучайте Каловрата! 💩')
