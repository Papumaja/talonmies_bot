from telegram import Update
from telegram.ext import CallbackContext

async def cmd_start(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Morjensta pöytään!")
