from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from game import GameManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot import Notifier

# Ваш токен от BotFather
TOKEN = '7176595145:AAEpjFe3rg4eDWj79K7LSNYTiNKZeorWHt8'

# Настройка базы данных
DATABASE_URL = 'sqlite:///board2game.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


main_menu_keyboard = [['Создать игру', 'Присоединиться к игре']]
in_game_keyboard = [['Следующий раунд', 'Остановить игру']]

main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, one_time_keyboard=False, resize_keyboard=True)
in_game_markup = ReplyKeyboardMarkup(in_game_keyboard, one_time_keyboard=False, resize_keyboard=True)

# Создаем экземпляр GameManager
notifier = Notifier(TOKEN)
game_manager = GameManager(session, notifier)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    chat_id = update.message.chat_id

    if text == 'Создать игру':
        await show_game_types(update, context)
    elif text in game_manager.get_available_game_types():
        await create_game(update, context, text)
    elif text == 'Присоединиться к игре':
        context.user_data['awaiting_code'] = True
        await update.message.reply_text('Пожалуйста, предоставьте код игры.', reply_markup=ReplyKeyboardMarkup([[]]))
    elif context.user_data.get('awaiting_code'):
        await join_game(update, context, text)
    elif text == 'Следующий раунд':
        await play_game(update, context)
    elif text == 'Остановить игру':
        await stop_game(update, context)
    else:
        await update.message.reply_text('Неизвестная команда. Пожалуйста, используйте меню.')

async def show_game_types(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    available_game_types = game_manager.get_available_game_types()
    game_type_keyboard = [[game_type] for game_type in available_game_types]
    game_type_markup = ReplyKeyboardMarkup(game_type_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Выберите тип игры:', reply_markup=game_type_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Создай новую игру или присоединись к текущей',
        reply_markup=main_menu_markup
    )

async def create_game(update: Update, context: ContextTypes.DEFAULT_TYPE, game_type: str) -> None:
    chat_id = update.message.chat_id
    code = game_manager.start(chat_id, game_type)
    await update.message.reply_text(f'Игра создана! Код игры: {code}', reply_markup=in_game_markup)


async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str) -> None:
    chat_id = update.message.chat_id
    message = game_manager.join(chat_id, code)
    await update.message.reply_text(message)
    context.user_data['awaiting_code'] = False

async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    message = await game_manager.play(chat_id)
    await update.message.reply_text(message)

async def stop_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    message = game_manager.stop(chat_id)
    await update.message.reply_text(message)

def main():
    # Создаем приложение
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    app.run_polling()

if __name__ == '__main__':
    main()
