import re
import math
from telegram import Update
from telegram.ext import CallbackContext

BASE_XP_TO_LVL = 30

def get_user_level(context, user_id):
    scores = context.chat_data.get('scores', None)
    if scores is not None:
        score = scores.get(user_id)
        if score is not None:
            return get_level(score)
    return 0

def get_xp(task_interval_s):
    return max(int(task_interval_s/60), 1)

def get_level(score):
    level = 0.0
    levelscore = score - BASE_XP_TO_LVL
    while levelscore > 0:
        levelscore -= (BASE_XP_TO_LVL + math.pow(level, 2))
        level += 1.0
    return int(level)

def generate_scoreboard(context: CallbackContext):
    scores = context.chat_data.get('scores', None)
    if scores is not None:
        sorted_s = {k: v for k, v in sorted(scores.items(), key = lambda a: a[1], reverse=True)}
        string = "Talonmiehistä parhaat:\n"
        for i, (id, score) in enumerate(sorted_s.items()):
            name_match = re.match(r'(@)(.*)', context.chat_data['users'][id])
            if name_match is not None:
                name = name_match.group(2)
            else:
                name = context.chat_data['users'][id]
            level = get_level(score)
            string += f"{i+1}. Lvl {level} {name} - {score} XP\n"
    else:
        return "Tyhjä!"
    return string

async def cmd_scoreboard(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id,
        text=generate_scoreboard(context))