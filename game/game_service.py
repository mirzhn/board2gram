from sqlalchemy.orm import Session
from .game_repository import GameRepository
from .base_game import Game

class GameService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = GameRepository(db)

    def get_open_game_codes(self):
        return self.repository.get_open_game_codes()

    def get_deck(self, game_type: str):
        return self.repository.get_deck(game_type)

    def save(self, game: Game):
        self.repository.save(game)

    def reload(self, code: str):
        return self.repository.load(code)
    
    def stop(self, game: Game):
        self.repository.stop(game)
