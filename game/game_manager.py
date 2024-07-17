from sqlalchemy.orm import Session
from .game import Game
from bot import Notifier

class GameManager:
    def __init__(self, db: Session, notifier: Notifier):
        self.db = db
        self.notifier = notifier
        self.games = {}

    def start_game(self, chat_id: int, game_type_name: str):
        if chat_id in self.games:
            return f"Game already in progress for chat {chat_id}"

        game = Game(self.db, game_type_name)
        game_code = game.create()
        self.games[chat_id] = game
        self.join_game(chat_id, True)
        return f"Started game with code {game_code} for chat {chat_id}"

    def join_game(self, chat_id: str, is_captain: bool = False):
        if chat_id not in self.games:
            return f"No game in progress for chat {chat_id}"

        game = self.games[chat_id]
        game.join(chat_id, is_captain)
        return f"Player {chat_id} joined game in chat {chat_id}"

    async def play(self, chat_id: int):
        if chat_id not in self.games:
            return "No game in progress for this chat"

        game = self.games[chat_id]
        messages = game.play()
        for chat_id, message in messages:
            await self.notifier.notify(chat_id, message)
        return f"Started the game for chat {chat_id}"

    def stop_game(self, chat_id: int):
        if chat_id in self.games:
            game = self.games[chat_id]
            game.stop()
            del self.games[chat_id]
            return f"Stopped game for chat {chat_id}"
        return f"No game in progress for chat {chat_id}"