import random
from telegram import Update
from telegram.ext import CallbackContext


def death_message():
    msgs = [
        "{} was shot by skeleton",
        "{} was pricked to death",
        "{} walked into a cactus whilst trying to escape creeper",
        "{} drowned",
        "{} experienced kinetic energy",
        "{} blew up",
        "{} was blown up by creeper",
        "{} was killed by Intentional Game Design",
        "{} hit the ground too hard",
        "{} fell from a high place",
        "{} fell off a ladder",
        "{} fell off some vines",
        "{} fell while climbing",
        "{} went up in flames",
        "{} burned to death",
        "{} tried to swim in lava",
        "{} was struck by lightning",
        "{} discovered the floor was lava",
        "{} was slain by zombie",
        "{} starved to death",
        "{} suffocated in a wall",
        "{} fell out of the world",
        "{} withered away",
        "{} died",
    ]
    return msgs[random.randint(0, len(msgs) - 1)]


async def cmd_spawn(update: Update, context):
    user = update.effective_user
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"``` Tervetuloa MuroCraftiin, {user.first_name}! Muistathan lukea säännöt :\)```",
        parse_mode="MarkdownV2",
    )


async def cmd_tp(update: Update, context):
    user = update.effective_user
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="``` " + death_message().format(user.first_name) + "```",
        parse_mode="MarkdownV2",
    )
