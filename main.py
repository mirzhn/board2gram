from game import GameManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot import Notifier, BotHandler
import logging
import logging.config
import os
import yaml
import time

logging.config.fileConfig('logging.conf')

logger = logging.getLogger(__name__)
def main():
    try:
        with open('config.yaml', 'r') as config_file:
            config = yaml.safe_load(config_file)

        TOKEN = config['telegram_bot']['token']
        DATABASE_URL = config['database']['url']

        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        notifier = Notifier(TOKEN)
        game_manager = GameManager(session, notifier)

        bot = BotHandler(game_manager, TOKEN)
        bot.run()
    
    except Exception as e:
        logger.exception("An error occurred during the execution of the bot")
        raise   
     
if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            logger.exception("Error in main loop")

    
