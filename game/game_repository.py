from sqlalchemy.orm import Session
from models import GameType, GameTypeCard, Game, Player, Round, RoundInfo, User
import datetime

class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_game_type_id(self, game_type_name: str) -> int:
        game_type = self.db.query(GameType).filter(GameType.name == game_type_name).first()
        if not game_type:
            raise ValueError(f"Game type '{game_type_name}' not found")
        return game_type.id

    def get_game_type_cards(self, game_type_id: int) -> list[GameTypeCard]:
        return self.db.query(GameTypeCard).filter(GameTypeCard.game_type_id == game_type_id).all()

    def create_game(self, game_type_id: int, code: str) -> Game:
        new_game = Game(game_type_id=game_type_id, code=code)
        self.db.add(new_game)
        self.db.commit()
        self.db.refresh(new_game)
        return new_game

    def get_game_by_code(self, code: str) -> Game:
        return self.db.query(Game).filter(Game.code == code).first()

    def add_player(self, chat_id: str, game_id: int, is_captain: bool = False) -> Player:
        user = self.db.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            new_user = User(chat_id=chat_id)  # Заполните другими необходимыми полями
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            user_id = new_user.id
        else:
            user_id = user.id
        
        new_player = Player(user_id=user_id, game_id=game_id, is_captain=is_captain)
        self.db.add(new_player)
        self.db.commit()
        self.db.refresh(new_player)
        return new_player

    def get_players_in_game(self, game_id: int) -> list[Player]:
        return self.db.query(Player).filter(Player.game_id == game_id).all()

    def create_round(self, game_id: int, num: int) -> Round:
        new_round = Round(game_id=game_id, num=num)
        self.db.add(new_round)
        self.db.commit()
        self.db.refresh(new_round)
        return new_round

    def add_round_info(self, round_id: int, key: str, value: str) -> RoundInfo:
        new_round_info = RoundInfo(round_id=round_id, key=key, value=value)
        self.db.add(new_round_info)
        self.db.commit()
        self.db.refresh(new_round_info)
        return new_round_info

    def get_used_card_ids(self, game_id: int) -> list[int]:
        used_card_infos = self.db.query(RoundInfo).join(Round).filter(Round.game_id == game_id, RoundInfo.key == 'used_card').all()
        return [int(info.value) for info in used_card_infos]
    
    def stop_game(self, game_id: int):
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if game:
            game.finish_dt = datetime.datetime.now()
            self.db.commit()