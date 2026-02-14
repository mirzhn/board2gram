from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from game.core.results import GameResult
from game.types import UserPayload

from . import texts
from .router import build_command_handlers


class BotConversation:
    def __init__(self, game_manager, markups):
        self.game_manager = game_manager
        self.markups = markups
        self.command_handlers = build_command_handlers(self)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = update.message.text
        handler = self.command_handlers.get(text)

        if handler:
            await handler(update, context)
            return

        if context.user_data.get("awaiting_code"):
            await self.join_game(update, context, text)
            return

        game_types = self.game_manager.get_available_game_types()
        if text in game_types.values():
            await self.create_game(update, context, text)
            return

        await update.message.reply_text(texts.MSG_UNKNOWN_COMMAND)

    async def await_game_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data["awaiting_code"] = True
        await update.message.reply_text(
            texts.MSG_ENTER_GAME_CODE, reply_markup=ReplyKeyboardMarkup([[]])
        )

    async def show_game_types(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        game_types = self.game_manager.get_available_game_types()
        game_type_keyboard = [[alias] for alias in game_types.values()]
        game_type_markup = ReplyKeyboardMarkup(
            game_type_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(texts.MSG_SELECT_GAME_TYPE, reply_markup=game_type_markup)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(texts.MSG_START, reply_markup=self.markups.main_menu)

    async def create_game(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, game_alias: str
    ) -> None:
        game_types = self.game_manager.get_available_game_types()
        game_type = next(key for key, alias in game_types.items() if alias == game_alias)
        user = UserPayload(
            chat_id=update.message.chat_id,
            name=update.message.from_user.first_name,
        )
        code = self.game_manager.start(user, game_type)
        await update.message.reply_text(
            texts.MSG_GAME_CREATED.format(code=code), reply_markup=self.markups.in_game_captain
        )

    async def join_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, code: str) -> None:
        user = UserPayload(
            chat_id=update.message.chat_id,
            name=update.message.from_user.first_name,
        )
        message = await self.game_manager.join(user, code)
        if message == GameResult.GAME_NOT_FOUND:
            await self.return_to_main_menu(update, context)
            context.user_data["awaiting_code"] = False
            return
        await update.message.reply_text(message, reply_markup=self.markups.in_game_player)
        context.user_data["awaiting_code"] = False

    async def play_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.play(chat_id)
        if message == GameResult.GAME_NOT_FOUND:
            await self.return_to_main_menu(update, context)

    async def stop_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.stop(chat_id)
        if message == GameResult.GAME_NOT_FOUND:
            await self.return_to_main_menu(update, context)
            return
        await update.message.reply_text(message, reply_markup=self.markups.main_menu)

    async def return_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            texts.MSG_RETURN_TO_MENU,
            reply_markup=self.markups.main_menu,
        )

    async def show_game_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        message = await self.game_manager.get_rules(chat_id)
        if message == GameResult.GAME_NOT_FOUND:
            await self.return_to_main_menu(update, context)
            return
        await update.message.reply_text(message)

    async def leave_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = UserPayload(
            chat_id=update.message.chat_id,
            name=update.message.from_user.first_name,
        )
        message = await self.game_manager.leave(user)
        if message == GameResult.GAME_NOT_FOUND:
            await self.return_to_main_menu(update, context)
            return
        await update.message.reply_text(message, reply_markup=self.markups.main_menu)
