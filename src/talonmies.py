import configparser

from telegram.ext import ApplicationBuilder, CommandHandler, PicklePersistence, BasePersistence

from .commands import *

class TalonmiesData(PicklePersistence):
    # TODO could implement custom SQL data storage inherited from BasePersistence
    # This currently will store everything in a pythonic pickle.
    pass


class Talonmies:

    def __init__(self, config_path):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(config_path)
        with open(self.cfg['API']['token_path'], 'r') as tokenfile:
            token = tokenfile.read().strip()
        
        self.data = TalonmiesData('./data/runtime.pickle')

        # Persistence makes the bot to store all internal variables on disk
        self.app = ApplicationBuilder().token(token).persistence(persistence=self.data).build()

        # Register command handlers
        start_handler = CommandHandler('start', cmd_start)
        self.app.add_handler(start_handler)
    
    def start(self):
        self.app.run_polling(stop_signals=None)

