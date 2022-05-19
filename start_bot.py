import asyncio
import logging
from src.talonmies import Talonmies

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    talonmies = Talonmies('config.ini')
    talonmies.start()
    
if __name__ == '__main__':
    main()