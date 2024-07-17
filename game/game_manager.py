from sqlalchemy.orm import Session
from .game import Game
from bot import Notifier

class GameManager:
    def __init__(self, db: Session, notifier: Notifier):
        self.db = db
        self.notifier = notifier
        self.games_by_chat = {}
        self.games_by_code = {}


    def start_game(self, chat_id: int, game_type_name: str):
        if chat_id in self.games_by_chat:
            return f"Game already in progress for chat {chat_id}"

        game = Game(self.db, game_type_name)
        game_code = game.create()
        self.games_by_code[game_code] = game
        self.games_by_chat[chat_id] = game
        self.join_game(chat_id, game_code, True)
        return game_code

    def join_game(self, user_id: int, game_code: str, is_captain: bool = False):
        if game_code not in self.games_by_code:
            return f"No game in progress with code {game_code}"

        game = self.games_by_code[game_code]
        game.join(user_id, is_captain)
        return f"Player {user_id} joined game with code {game_code}"

    async def play(self, chat_id: int):
        if chat_id not in self.games_by_chat:
            return "No game in progress for this chat"

        game = self.games_by_chat[chat_id]
        messages = game.play()
        for chat_id, message in messages:
            await self.notifier.notify(chat_id, message)
        return f"Started the game for chat {chat_id}"

    def stop_game(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            game.stop()
            del self.games_by_chat[chat_id]
            return f"Stopped game for chat {chat_id}"
        return f"No game in progress for chat {chat_id}"