from sqlalchemy.orm import Session
from .game_factory import GameFactory
from .game_service import GameService 
from .chameleon_game import ChameleonGame
from .base_game import Game
import random
import string

class GameManager:
    def __init__(self, db: Session, notifier):
        self.factory = GameFactory()
        self.db = db
        self.game_service = GameService(db)
        self.notifier = notifier
        self.games_by_code = {}
        self.games_by_chat = {}
        self.register_game('chameleon', ChameleonGame, 'Заяц')

    def register_game(self, game_name, game_class, alias):
        self.factory.register_game(game_name, game_class, alias)

    def create_game(self, game_name, *args, **kwargs):
        return self.factory.get_game(game_name, *args, **kwargs)
    
    def generate_code(self, existing_codes):
        while True:
            code = ''.join(random.choices(string.digits, k=4))
            if code not in existing_codes:
                return code

    def start(self, user: list, game_type: str):
        existing_codes = self.game_service.get_open_game_codes()
        code = self.generate_code(existing_codes)
        deck = self.game_service.get_deck(game_type)
        game = self.create_game('chameleon', deck, user, code, game_type)
        self.games_by_code[code] = game
        self.games_by_chat[user['chat_id']] = game
        return code

    async def join(self, user: list, code: str):
        if code in self.games_by_code:
            game = self.games_by_code[code]
            game.join(user)
            self.games_by_chat[user['chat_id']] = game
            await self.notify_captain(game, f'игрок {user['name']} присоединился к игре')
            return f"Player {user['chat_id']} joined game with code {code}"
        else:
            return "Game not exist"

    async def play(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            messages = game.play()

            for _chat_id, message in messages:
                await self.notifier.notify(_chat_id, message)     
        else:
            return "Game not exist"
        return f"Started the game for chat {chat_id}"

    def save(self, game: Game):
        self.game_service.save(game)

    def reload(self, code: str):
        game = self.game_service.reload(code)
        if game:
            self.games_by_code[code] = game
            return game
        else:
            return None

    async def stop(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            self.save(game)
            self.game_service.stop(game)
            del self.games_by_chat[chat_id]
            await self.notify_all_players(game, "Игра завершена! спасибо за игру")
            return f"Stopped game for chat {chat_id}"
        else:
            return "Game not exist"
        
    def get_available_game_types(self):
        return self.factory.get_available_game_types()
    
    async def notify_all_players(self, game: Game, message: str):
        for player in game.players:
            await self.notifier.notify(player['user_id'], message)

    async def notify_captain(self, game: Game, message: str):
        await self.notifier.notify(game.captain_id, message)

    async def get_rules(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            return game.get_rules()
        else:
            return "Game not exist"
        
    async def leave(self, user: list):
        if user['chat_id'] in self.games_by_chat:
            game = self.games_by_chat[user['chat_id']]
            game.leave(user)
            await self.notify_captain(game, f'игрок {user['name']} покинул игру')
            return f"Player {user['chat_id']} leave game"
        else:
            return "Game not exist"