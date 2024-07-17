from sqlalchemy.orm import Session
from .game_repository import GameRepository
import random
import string

class GameService:
    def __init__(self, db: Session):
        self.repository = GameRepository(db)

    def generate_game_code(self, length=4):
        return ''.join(random.choices(string.digits, k=length))

    def create_game(self, game_type_name: str):
        game_type_id = self.repository.get_game_type_id(game_type_name)
        code = self.generate_game_code()
        return self.repository.create_game(game_type_id, code)

    def join_game(self, chat_id: string, is_captain: bool, game_id: int):
        self.repository.add_player(chat_id, game_id, is_captain)

    def get_game_by_code(self, game_code: str):
        return self.repository.get_game_by_code(game_code)

    def get_players_in_game(self, game_id: int):
        return self.repository.get_players_in_game(game_id)

    def get_game_type_cards(self, game_type_name: str):
        game_type_id = self.repository.get_game_type_id(game_type_name)
        return self.repository.get_game_type_cards(game_type_id)

    def start_round(self, game_id: int, round_num: int):
        return self.repository.create_round(game_id, round_num)

    def add_round_info(self, round_id: int, key: str, value: str):
        self.repository.add_round_info(round_id, key, value)

    def get_used_card_ids(self, game_id: int):
        return self.repository.get_used_card_ids(game_id)
    
    def stop_game(self, game_id: int):
        self.repository.stop_game(game_id)
