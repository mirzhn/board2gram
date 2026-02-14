import random
import string

from sqlalchemy.orm import Session

from ..base_game import GameSession
from ..modes.bunker import BunkerGame
from ..modes.chameleon import ChameleonGame
from ..modes.ilito import IlitoGame
from ..types import UserPayload
from .factory import GameFactory
from .results import GameResult
from .service import GameService


class GameManager:
    def __init__(self, db: Session, notifier):
        self.factory = GameFactory()
        self.db = db
        self.game_service = GameService(db)
        self.notifier = notifier
        self.games_by_code: dict[str, GameSession] = {}
        self.games_by_chat: dict[int, GameSession] = {}
        self.register_game("chameleon", ChameleonGame, "Заяц")
        self.register_game("bunker", BunkerGame, "Бункер")
        self.register_game("ilito", IlitoGame, "Илито")

    def register_game(self, game_name, game_class, alias):
        self.factory.register_game(game_name, game_class, alias)

    def create_game(self, game_name, *args, **kwargs):
        return self.factory.get_game(game_name, *args, **kwargs)

    def generate_code(self, existing_codes):
        while True:
            code = "".join(random.choices(string.digits, k=4))
            if code not in existing_codes:
                return code

    def start(self, user: UserPayload, game_type: str):
        user_payload = UserPayload.from_any(user)
        existing_codes = self.game_service.get_open_game_codes()
        code = self.generate_code(existing_codes)
        deck = self.game_service.get_deck(game_type)
        game = self.create_game(game_type, deck, user_payload, code, game_type)
        self.games_by_code[code] = game
        self.games_by_chat[user_payload.chat_id] = game
        return code

    async def join(self, user: UserPayload, code: str):
        user_payload = UserPayload.from_any(user)
        if code in self.games_by_code:
            game = self.games_by_code[code]
            game.join(user_payload)
            self.games_by_chat[user_payload.chat_id] = game
            await self.notify_captain(game, f"игрок {user_payload.name} присоединился к игре")
            return f"Вы присоединились к игре с кодом {code}"
        return GameResult.GAME_NOT_FOUND

    async def play(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            messages = game.play()
            for _chat_id, message in messages:
                await self.notifier.notify(_chat_id, message)
            return None
        return GameResult.GAME_NOT_FOUND

    def save(self, game: GameSession):
        self.game_service.save(game)

    def reload(self, code: str):
        game = self.game_service.reload(code)
        if game:
            self.games_by_code[code] = game
            return game
        return None

    async def stop(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            self.save(game)
            self.game_service.stop(game)
            del self.games_by_chat[chat_id]
            await self.notify_all_players(game, "Игра завершена! спасибо за игру")
            return "Спасибо за игру, капитан!"
        return GameResult.GAME_NOT_FOUND

    def get_available_game_types(self):
        return self.factory.get_available_game_types()

    async def notify_all_players(self, game: GameSession, message: str):
        for player in game.players:
            await self.notifier.notify(player.user_id, message)

    async def notify_captain(self, game: GameSession, message: str):
        await self.notifier.notify(game.captain_id, message)

    async def get_rules(self, chat_id: int):
        if chat_id in self.games_by_chat:
            game = self.games_by_chat[chat_id]
            return game.get_rules()
        return GameResult.GAME_NOT_FOUND

    async def leave(self, user: UserPayload):
        user_payload = UserPayload.from_any(user)
        if user_payload.chat_id in self.games_by_chat:
            game = self.games_by_chat[user_payload.chat_id]
            game.leave(user_payload)
            await self.notify_captain(game, f"игрок {user_payload.name} покинул игру")
            return "Вы вышли из игры"
        return GameResult.GAME_NOT_FOUND
