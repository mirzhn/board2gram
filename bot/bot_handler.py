from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


class BotHandler:
    def __init__(self, game_manager, TOKEN):

        self.main_menu_keyboard = [['Создать игру', 'Присоединиться к игре']]
        self.in_game_keyboard = [['Следующий раунд', 'Остановить игру']]
        self.main_menu_markup = ReplyKeyboardMarkup(self.main_menu_keyboard, one_time_keyboard=False, resize_keyboard=True)
        self.in_game_markup = ReplyKeyboardMarkup(self.in_game_keyboard, one_time_keyboard=False, resize_keyboard=True)

        self.game_manager = game_manager
        self.TOKEN = TOKEN


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = update.message.text

        if text == 'Создать игру':
            await self.show_game_types(update, context)
        elif text in self.game_manager.get_available_game_types():
            await self.create_game(update, context, text)
        elif text == 'Присоединиться к игре':
            context.user_data['awaiting_code'] = True
            await update.message.reply_text('Пожалуйста, предоставьте код игры.', reply_markup=ReplyKeyboardMarkup([[]]))
        elif context.user_data.get('awaiting_code'):
            await self.join_game(update, context, text)
        elif text == 'Следующий раунд':
            await self.play_game(update, context)
        elif text == 'Остановить игру':
            await self.stop_game(update, context)
        else:
            await update.message.reply_text('Неизвестная команда')

    async def show_game_types(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        game_types = self.game_manager.get_available_game_types()
        game_type_keyboard = [[game_type] for game_type in game_types]
        game_type_markup = ReplyKeyboardMarkup(game_type_keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Выберите тип игры:', reply_markup=game_type_markup)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            f'Привет! Создай новую игру или присоединись к текущей',
            reply_markup=self.main_menu_markup
        )

    async def create_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, game_type: str) -> None:
        user = {}
        user['chat_id'] = update.message.chat_id
        user['name'] = update.message.from_user.first_name
        code = self.game_manager.start(user, game_type)
        await update.message.reply_text(f'Игра создана! Код игры: {code}', reply_markup=self.in_game_markup)

    async def join_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, code: str) -> None:
        user = {}
        user['chat_id'] = update.message.chat_id
        user['name'] = update.message.from_user.first_name
        message = await self.game_manager.join(user, code)
        await update.message.reply_text(message)
        context.user_data['awaiting_code'] = False

    async def play_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.play(chat_id)
        await update.message.reply_text(message)

    async def stop_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.stop(chat_id)
        await update.message.reply_text(message)

    def run(self):
        # Создаем приложение
        app = ApplicationBuilder().token(self.TOKEN).build()

        # Добавляем обработчики команд
        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Запускаем бота
        app.run_polling()
