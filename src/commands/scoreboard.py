from telegram import Update
from telegram.ext import CallbackContext

def generate_scoreboard(context: CallbackContext):
    scores = context.chat_data.get('scores', None)
    if scores is not None:
        sorted_s = {k: v for k, v in sorted(scores.items(), key = lambda a: a[1], reverse=True)}
        string = "Talonmiehistä parhaat:\n"
        for i, (id, score) in enumerate(sorted_s.items()):
            name = context.chat_data['users'][id]
            string += f"{i+1}. {name} - {score} XP\n"
    else:
        return "Tyhjä!"
    return string

async def cmd_scoreboard(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
        text=generate_scoreboard(context))