from sqlalchemy.orm import Session

from .repository_read import GameRepositoryReader
from .repository_write import GameRepositoryWriter


class GameRepository:
    def __init__(self, db: Session):
        self.db = db
        self.reader = GameRepositoryReader(db)
        self.writer = GameRepositoryWriter(db)

    def get_open_game_codes(self):
        return self.reader.get_open_game_codes()

    def get_deck(self, game_type_name: str):
        return self.reader.get_deck(game_type_name)

    def save(self, game):
        return self.writer.save(game)

    def load(self, code: str):
        return self.reader.load(code)

    def stop(self, game):
        return self.writer.stop(game)
