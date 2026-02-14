import logging

from telegram import Bot


logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)

    async def notify(self, user_id: int, message: str):
        try:
            await self.bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
        except Exception:
            logger.exception("Failed to send message to chat_id=%s", user_id)
