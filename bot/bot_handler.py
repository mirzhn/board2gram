from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from .conversation import BotConversation
from .keyboards import build_markups


class BotHandler:
    def __init__(self, game_manager, token: str):
        self.token = token
        self.conversation = BotConversation(game_manager=game_manager, markups=build_markups())

    def run(self):
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.conversation.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.conversation.handle_message))
        app.run_polling()
