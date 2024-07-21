from sqlalchemy.orm import Session
from .game_service import GameService
from .game import Game
from bot import Notifier
import random
import string

class GameManager:
    def __init__(self, db: Session, notifier):
        self.db = db
        self.game_service = GameService(db)
        self.notifier = notifier
        self.games_by_code = {}
        self.games_by_chat = {}

    def generate_game_code(self, existing_codes):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if code not in existing_codes:
                return code

    def start_game(self, chat_id: int, game_type_name: str):
        existing_codes = self.game_service.get_open_game_codes()
        game_code = self.generate_game_code(existing_codes)
        deck = self.game_service.get_game_deck(game_type_name)
        game = Game(deck, chat_id, game_code, game_type_name)
        self.games_by_code[game_code] = game
        self.games_by_chat[chat_id] = game
        self.save_game(game)
        return game_code

    def join_game(self, user_id: int, game_code: str):
        if game_code in self.games_by_code:
            game = self.games_by_code[game_code]
            game.join(user_id)
            self.save_game(game)
            return f"Player {user_id} joined game with code {game_code}"
        else:
            return f"No game found with code {game_code}"

    async def play_game(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            messages = game.play()
            self.save_game(game)

            for chat_id, message in messages:
                await self.notifier.notify(chat_id, message)     
        else:
            return f"No game found with code {game_code}"
        return f"Started the game for chat {chat_id}"

    def save_game(self, game: Game):
        self.game_service.save(game)

    def reload_game(self, game_code: str):
        game = self.game_service.reload(game_code)
        if game:
            self.games_by_code[game_code] = game
            return game
        else:
            return None
