from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Game, Player, Round, RoundInfo, GameType, GameTypeCard, User
import datetime


class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_open_game_codes(self):
        games = self.db.query(Game).filter(Game.finish_dt == None).all()
        return [game.code for game in games]

    def get_game_deck(self, game_type_name: str):
        game_type = self.db.query(GameType).filter(GameType.name == game_type_name).first()
        if not game_type:
            raise ValueError(f"Game type '{game_type_name}' not found")
        cards = self.db.query(GameTypeCard).filter(GameTypeCard.game_type_id == game_type.id).all()
        return [{'id': card.id, 'key': card.key, 'value': card.value} for card in cards]

    def save_game(self, game: Game):
        game_record = self.db.query(Game).filter(Game.code == game.code, Game.finish_dt == None).first()
        if not game_record:
            game_record = Game(code=game.code, game_type_id=self.get_game_type_id(game.game_type_name), start_dt=datetime.datetime.now())
            self.db.add(game_record)
            self.db.commit()
            self.db.refresh(game_record)

        # Save users
        for player in game.players:
            user_record = self.db.query(User).filter(User.chat_id == player['user_id']).first()
            if not user_record:
                new_user = User(chat_id=player['user_id'])  # Дополните другими необходимыми полями
                self.db.add(new_user)
                self.db.commit()
                self.db.refresh(new_user)

        # Save players
        for player in game.players:
            user_record = self.db.query(User).filter(User.chat_id == player['user_id']).first()
            player_record = self.db.query(Player).filter(Player.game_id == game_record.id, Player.user_id == user_record.id).first()
            if not player_record:
                player_record = Player(game_id=game_record.id, user_id=user_record.id, is_captain=player['is_captain'])
                self.db.add(player_record)
            self.db.commit()
        # Save rounds
        for round_num in range(1, game.round + 1):
            round_record = self.db.query(Round).filter(Round.game_id == game_record.id, Round.num == round_num).first()
            if not round_record:
                round_record = Round(game_id=game_record.id, num=round_num)
                self.db.add(round_record)
            self.db.commit()

            # Save round info using merge
        for round_info in game.round_info:
            round_record = self.db.query(Round).filter(Round.game_id == game_record.id, Round.num == round_info['round_id']).first()
            round_info_record = self.db.query(RoundInfo).filter(RoundInfo.round_id == round_record.id, RoundInfo.key == round_info['key']).first()
            if not round_info_record:
                round_info_record = RoundInfo(round_id=round_record.id, key=round_info['key'], value=round_info['value'])
                self.db.add(round_info_record)
            self.db.commit()

    def load_game(self, game_code: str):
        game_record = self.db.query(Game).filter(Game.code == game_code, Game.finish_dt == None).first()
        if not game_record:
            return None
        
        players = self.db.query(Player).filter(Player.game_id == game_record.id).all()
        player_list = [{'user_id': player.user_id, 'role': 'player', 'is_captain': player.is_captain} for player in players]
        deck = self.get_game_deck(game_record.game_type.name)

        max_round = self.db.query(func.max(Round.num)).filter(Round.game_id == game_record.id).scalar()

        round_info_records = self.db.query(RoundInfo).join(Round).filter(Round.game_id == game_record.id).all()
        round_info_list = [{'round_id': round_info.round_id, 'key': round_info.key, 'value': round_info.value} for round_info in round_info_records]

        game = Game(
            code=game_record.code,
            game_type_name=game_record.game_type.name,
            players=player_list,
            round=max_round,
            round_info=round_info_list, 
            deck=deck
        )

        return game

    def get_game_type_id(self, game_type_name: str) -> int:
        game_type = self.db.query(GameType).filter(GameType.name == game_type_name).first()
        if not game_type:
            raise ValueError(f"Game type '{game_type_name}' not found")
        return game_type.id
    
    def stop_game(self, game: Game):
        game_record = self.db.query(Game).filter(Game.code == game.code, Game.finish_dt == None).first()
        if not game_record:
            raise ValueError(f"Game with code '{game.code}' not found")
        game_record.finish_dt = datetime.datetime.now()
        self.db.commit()
