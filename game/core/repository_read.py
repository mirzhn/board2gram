from sqlalchemy import func
from sqlalchemy.orm import Session

from models import (
    Game as GameModel,
    GameType,
    GameTypeCard,
    Player,
    Round,
    RoundInfo,
    User,
)

from ..base_game import GameSession
from ..types import Card, PlayerState, RoundInfoEntry, UserPayload


class GameRepositoryReader:
    def __init__(self, db: Session):
        self.db = db

    def get_open_game_codes(self) -> list[str]:
        games = self.db.query(GameModel).filter(GameModel.finish_dt.is_(None)).all()
        return [game.code for game in games]

    def get_deck(self, game_type_name: str) -> list[Card]:
        game_type = self.db.query(GameType).filter(GameType.name == game_type_name).first()
        if not game_type:
            raise ValueError(f"Game type '{game_type_name}' not found")
        cards = self.db.query(GameTypeCard).filter(GameTypeCard.game_type_id == game_type.id).all()
        return [Card(id=card.id, key=card.key, value=card.value) for card in cards]

    def load(self, code: str):
        game_record = (
            self.db.query(GameModel)
            .filter(GameModel.code == code, GameModel.finish_dt.is_(None))
            .first()
        )
        if not game_record:
            return None

        player_records = (
            self.db.query(Player, User)
            .join(User, Player.user_id == User.id)
            .filter(Player.game_id == game_record.id)
            .all()
        )
        player_list = [
            PlayerState(
                user_id=int(player_user.chat_id),
                name=player_user.name,
                role="player",
                is_captain=player.is_captain,
            )
            for player, player_user in player_records
        ]

        deck = self.get_deck(game_record.game_type.name)
        max_round = self.db.query(func.max(Round.num)).filter(Round.game_id == game_record.id).scalar()
        current_round = max_round or 0

        captain = next((player for player in player_list if player.is_captain), None)
        if captain is None and player_list:
            captain = player_list[0]
        if captain is None:
            return None

        runtime_game = GameSession(
            deck=deck,
            user=UserPayload(chat_id=captain.user_id, name=captain.name),
            code=game_record.code,
            game_type=game_record.game_type.name,
            players=[],
            round=current_round,
        )
        runtime_game.players = player_list

        round_info_records = (
            self.db.query(RoundInfo, Round)
            .join(Round, RoundInfo.round_id == Round.id)
            .filter(Round.game_id == game_record.id)
            .all()
        )
        runtime_game.round_info = [
            RoundInfoEntry(round_id=round.num, key=round_info.key, value=round_info.value)
            for round_info, round in round_info_records
        ]

        return runtime_game
