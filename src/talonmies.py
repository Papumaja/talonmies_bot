import configparser

from telegram.ext import ApplicationBuilder, CommandHandler,\
    CallbackQueryHandler, PicklePersistence, BasePersistence,\
    CallbackContext, Application

from .commands import *

class TalonmiesData(PicklePersistence):
    # TODO could implement custom SQL data storage inherited from BasePersistence
    # This currently will store everything in a pythonic pickle.
    pass

async def post_init(app):
    # Restart jobs
    for id, chat_data in app.chat_data.items():
        context = CallbackContext(app, chat_id=id)
        await context.bot.send_message(chat_id=id,
            text="Morjensta pöytään! Adminit käynnisteli uuestaan, teiän jobien intervallit"\
                +" alkaa kans nyt uusiks, käyttäkää /task hetinyt <nimi> jos oli kohta tulossa :D")
        if 'tasks' in chat_data:
            for task in chat_data['tasks'].values():
                if task.running:
                    print(f'Restarting task {task.name} in chat {id}')
                    task.start(context, id)


class Talonmies:

    commands = {
        'start': cmd_start,
        'task': cmd_task,
        'scoreboard': cmd_scoreboard,
        'tp': cmd_tp,
        'spawn': cmd_spawn,
        'wildu': cmd_wildu
    }

    def __init__(self, config_path):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(config_path)
        with open(self.cfg['API']['token_path'], 'r') as tokenfile:
            token = tokenfile.read().strip()
        
        self.data = TalonmiesData('./data/runtime.pickle')

        # Persistence makes the bot to store all internal variables on disk
        self.app = Application.builder().token(token).persistence(persistence=self.data).post_init(post_init).build()

        # Register command handlers
        for cmd_string, cmd_bind in Talonmies.commands.items():
            handler = CommandHandler(cmd_string, cmd_bind)
            self.app.add_handler(handler)
        self.app.add_handler(CallbackQueryHandler(buttons.button_handler))

    
    def start(self):
        self.app.run_polling(stop_signals=None)

