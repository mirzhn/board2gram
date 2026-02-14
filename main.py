import logging
import logging.config
import signal
import sys

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot import BotHandler, Notifier
from game import GameManager

logging.config.fileConfig('logging.conf')

logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    logger.info("Received signal to terminate. Exiting...")
    sys.exit(0)


def main():
    try:
        with open("config.yaml", "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        token = config["telegram_bot"]["token"]
        database_url = config["database"]["url"]

        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        notifier = Notifier(token)
        game_manager = GameManager(session, notifier)

        bot = BotHandler(game_manager, token)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        bot.run()
    except Exception:
        logger.exception("An error occurred during the execution of the bot")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Error in main loop")
