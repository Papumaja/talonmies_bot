import configparser

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    PicklePersistence,
    BasePersistence,
    CallbackContext,
    Application,
    MessageHandler,
    PollAnswerHandler,
    filters,
)
from telegram.error import Forbidden
from .handlers.scran_reader import validate_save_msg_scrans, ScranFilter
from .commands.scrandle import handle_scran_poll_update
from .database import create_db_and_tables

from .commands import *


class TalonmiesData(PicklePersistence):
    # TODO could implement custom SQL data storage inherited from BasePersistence
    # This currently will store everything in a pythonic pickle.
    pass


async def post_init(app):
    # Restart jobs

    for id, chat_data in app.chat_data.items():
        context = CallbackContext(app, chat_id=id)
        try:
            await context.bot.send_message(
                chat_id=id,
                text="Morjensta pöytään! Adminit käynnisteli uuestaan, teiän jobien intervallit"
                + " alkaa kans nyt uusiks, käyttäkää /task hetinyt <nimi> jos oli kohta tulossa :D",
            )
        except Forbidden:
            print("Someone has blocked the bot lol")

        if "tasks" in chat_data:
            for task in chat_data["tasks"].values():
                if task.running:
                    print(f"Restarting task {task.name} in chat {id}")
                    task.start(context, id)


class Talonmies:

    commands = {
        "start": cmd_start,
        "task": cmd_task,
        "scoreboard": cmd_scoreboard,
        "tp": cmd_tp,
        "spawn": cmd_spawn,
        "wildu": cmd_wildu,
        "scrandle": cmd_scrandle,
        "scrandle_stop": cmd_close_scrandle_poll,
        "scrandle_top": cmd_scrandle_result,
        "scrandle_info": cmd_scrandle_info,
        "scrandle_time": cmd_scrandle_timed,
    }

    def __init__(self, config):
        self.data = TalonmiesData("./data/runtime.pickle")
        create_db_and_tables()
        # Persistence makes the bot to store all internal variables on disk
        self.app = (
            Application.builder()
            .token(config['API']['bot_token'])
            .persistence(persistence=self.data)
            .post_init(post_init)
            .build()
        )

        # Register command handlers
        for cmd_string, cmd_bind in Talonmies.commands.items():
            handler = CommandHandler(cmd_string, cmd_bind)
            self.app.add_handler(handler)
        self.app.add_handler(CallbackQueryHandler(buttons.button_handler))

        ## SCRANDLE
        scran_filter = ScranFilter()
        self.app.add_handler(
            MessageHandler(scran_filter & filters.PHOTO, validate_save_msg_scrans)
        )
        self.app.add_handler(PollAnswerHandler(handle_scran_poll_update))

    def start(self):
        self.app.run_polling(stop_signals=None)
