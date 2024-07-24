#from telegram import Bot

class Notifier:
    def __init__(self, bot_token: str):
        self.t = 1
        #self.bot = Bot(token=bot_token)

    async def notify(self, user_id: int, message: str):
        try:
            #await self.bot.send_message(chat_id=user_id, text=message)
            print(f"send to {user_id} message:{message}")
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")
