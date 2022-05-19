from telegram import Update
from telegram.ext import CallbackContext

async def warning_wrong_number_of_args(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Väärä määrä argumentteja, pöljä.")

async def warning_no_tasks(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ei tehtäviä!")

async def warning_unknown(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Häh?")

async def warning_no_task(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
        text=f"Tehtävää ei ole olemassa!")