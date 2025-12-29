import asyncio
import configparser

import logging
from src.talonmies import Talonmies

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    parser = configparser.ConfigParser()
    parser.read('config.ini')
    talonmies = Talonmies(parser)
    talonmies.start()
    
if __name__ == '__main__':
    main()