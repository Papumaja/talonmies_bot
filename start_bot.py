import asyncio
from dotenv import dotenv_values

import logging
from src.talonmies import Talonmies

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

config = dotenv_values(".env")

def main():
    talonmies = Talonmies(config)
    talonmies.start()
    
if __name__ == '__main__':
    main()