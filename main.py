from game import GameManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot import Notifier, BotHandler
import yaml

if __name__ == '__main__':
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
