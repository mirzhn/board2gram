import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from game import GameManager
from bot import Notifier


# Конфигурация базы данных и бота
DATABASE_URL = 'sqlite:///board2game.db'
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'

# Настройка SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Инициализация Notifier
notifier = Notifier(TELEGRAM_BOT_TOKEN)

def main():
    with SessionLocal() as db:
        # Инициализация GameManager
        game_manager = GameManager(db, notifier)

        chat_id = 123456789  # Замените на ваш chat_id
        game_type_name = 'chameleon'
        print(game_manager.start_game(chat_id, game_type_name))


if __name__ == '__main__':
    main()