from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


class BotHandler:
    def __init__(self, game_manager, TOKEN):

        self.main_menu_keyboard = [['Создать игру', 'Присоединиться к игре']]
        self.in_game_captain_keyboard = [['Правила игры','Следующий раунд', 'Остановить игру']]
        self.in_game_player_keyboard = [['Правила игры', 'Выйти из игры']]
        self.main_menu_markup = ReplyKeyboardMarkup(self.main_menu_keyboard, one_time_keyboard=False, resize_keyboard=True)
        self.in_game_captain_markup = ReplyKeyboardMarkup(self.in_game_captain_keyboard, one_time_keyboard=False, resize_keyboard=True)
        self.in_game_player_markup = ReplyKeyboardMarkup(self.in_game_player_keyboard, one_time_keyboard=False, resize_keyboard=True)

        self.game_manager = game_manager
        self.TOKEN = TOKEN

        # Словарь для сопоставления команд и их обработчиков
        self.command_handlers = {
            'Создать игру': self.show_game_types,
            'Присоединиться к игре': self.await_game_code,
            'Следующий раунд': self.play_game,
            'Остановить игру': self.stop_game,
            'Правила игры': self.show_game_rules,
            'Выйти из игры': self.leave_game
        }


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = update.message.text

        handler = self.command_handlers.get(text)

        if handler:
            await handler(update, context)
        elif context.user_data.get('awaiting_code'):
            await self.join_game(update, context, text)
        else:
            game_types = self.game_manager.get_available_game_types()
            print(game_types)
            if text in game_types.values():
                await self.create_game(update, context, text)
            else:
                await update.message.reply_text('Неизвестная команда')

    async def await_game_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data['awaiting_code'] = True
        await update.message.reply_text('Пожалуйста, предоставьте код игры.', reply_markup=ReplyKeyboardMarkup([[]]))

    async def show_game_types(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        game_types = self.game_manager.get_available_game_types()
        game_type_keyboard = [[alias] for alias in game_types.values()]
        game_type_markup = ReplyKeyboardMarkup(game_type_keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Выберите тип игры:', reply_markup=game_type_markup)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            f'Привет! Создай новую игру или присоединись к текущей',
            reply_markup=self.main_menu_markup
        )

    async def create_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, game_alias: str) -> None:
        game_types = self.game_manager.get_available_game_types()
        game_type = next(key for key, alias in game_types.items() if alias == game_alias)
        user = {
            'chat_id': update.message.chat_id,
            'name': update.message.from_user.first_name
        }
        code = self.game_manager.start(user, game_type)
        await update.message.reply_text(f'Игра создана! Код игры: {code}', reply_markup=self.in_game_captain_markup)

    async def join_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, code: str) -> None:
        user = {
            'chat_id': update.message.chat_id,
            'name': update.message.from_user.first_name
        }
        message = await self.game_manager.join(user, code)
        await update.message.reply_text(message, reply_markup=self.in_game_player_markup)
        context.user_data['awaiting_code'] = False

    async def play_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.play(chat_id)
        if message == "Game not exist":
            await self.return_to_main_menu(update, context, message)
        else:
            await update.message.reply_text(message)

    async def stop_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.stop(chat_id)
        if message == "Game not exist":
            await self.return_to_main_menu(update, context, message)
        else:
            await update.message.reply_text(message, reply_markup=self.main_menu_markup)

    async def return_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
        await update.message.reply_text('Что-то пошло не так. Попробуйте создать или присоединиться к игре', reply_markup=self.main_menu_markup)

    async def show_game_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.get_rules(chat_id)
        if message == "Game not exist":
            await self.return_to_main_menu(update, context, message)
        else:
            await update.message.reply_text(message)

    async def leave_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = {
            'chat_id': update.message.chat_id,
            'name': update.message.from_user.first_name
        }
        message = await self.game_manager.leave(user)
        if message == "Game not exist":
            await self.return_to_main_menu(update, context, message)
        else:
            await update.message.reply_text(message, reply_markup=self.main_menu_markup)

    def run(self):
        # Создаем приложение
        app = ApplicationBuilder().token(self.TOKEN).build()

        # Добавляем обработчики команд
        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Запускаем бота
        app.run_polling()
