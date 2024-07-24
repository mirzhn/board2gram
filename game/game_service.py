from sqlalchemy.orm import Session
from .game_repository import GameRepository
from .game import Game

class GameService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = GameRepository(db)

    def get_open_game_codes(self):
        return self.repository.get_open_game_codes()

    def get_game_deck(self, game_type_name: str):
        return self.repository.get_game_deck(game_type_name)

    def save(self, game: Game):
        self.repository.save_game(game)

    def reload(self, game_code: str):
        return self.repository.load_game(game_code)
    
    def stop(self, game: Game):
        self.repository.stop_game(game)
