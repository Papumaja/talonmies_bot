from telegram import Update
from telegram.ext import CallbackContext


GITHUB_URL = "https://github.com/Papumaja/talonmies_bot"


async def cmd_start(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Morjensta pöytään!")


async def cmd_feature_request(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Koodaa ite ja tee PR: {GITHUB_URL}")