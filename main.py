import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from game import GameManager
from bot import Notifier
import time


# Конфигурация базы данных и бота
DATABASE_URL = 'sqlite:///board2game.db'
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'

# Настройка SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Инициализация Notifier
notifier = Notifier(TELEGRAM_BOT_TOKEN)

async def main():
    with SessionLocal() as db:
        # Инициализация GameManager
        game_manager = GameManager(db, notifier)

        chat_id_1 = 123456789  # Замените на ваш chat_id
        chat_id_2 = 553555555  # Замените на ваш chat_id
        game_type_name = 'chameleon'
        game_code = game_manager.start_game(chat_id_1, game_type_name)
        print(game_manager.join_game(chat_id_2, game_code))

        await game_manager.play(chat_id_1)

        await game_manager.play(chat_id_1)

        await game_manager.play(chat_id_1)

        await game_manager.play(chat_id_1)

        #time.sleep(3) 
        print(game_manager.stop_game(chat_id_1))

if __name__ == '__main__':
    asyncio.run(main())