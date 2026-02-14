import datetime

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


class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_open_game_codes(self):
        games = self.db.query(GameModel).filter(GameModel.finish_dt.is_(None)).all()
        return [game.code for game in games]

    def get_deck(self, game_type_name: str):
        game_type = self.db.query(GameType).filter(GameType.name == game_type_name).first()
        if not game_type:
            raise ValueError(f"Game type '{game_type_name}' not found")
        cards = self.db.query(GameTypeCard).filter(GameTypeCard.game_type_id == game_type.id).all()
        return [Card(id=card.id, key=card.key, value=card.value) for card in cards]

    def save(self, game: GameSession):
        try:
            game_record = self._get_or_create_open_game_record(game)
            users_by_chat_key = self._get_or_create_users(game.players)
            self._ensure_players(game_record.id, game.players, users_by_chat_key)
            rounds_by_num = self._ensure_rounds(game_record.id, game.round)
            self._ensure_round_info(game_record.id, rounds_by_num, game.round_info)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

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

    def get_game_type_id(self, game_type_name: str) -> int:
        game_type = self.db.query(GameType).filter(GameType.name == game_type_name).first()
        if not game_type:
            raise ValueError(f"Game type '{game_type_name}' not found")
        return game_type.id

    def stop(self, game: GameSession):
        game_record = (
            self.db.query(GameModel)
            .filter(GameModel.code == game.code, GameModel.finish_dt.is_(None))
            .first()
        )
        if not game_record:
            raise ValueError(f"Game with code '{game.code}' not found")
        game_record.finish_dt = datetime.datetime.now()
        self.db.commit()

    def _chat_key(self, chat_id) -> str:
        return str(chat_id)

    def _get_or_create_open_game_record(self, game: GameSession):
        game_record = (
            self.db.query(GameModel)
            .filter(GameModel.code == game.code, GameModel.finish_dt.is_(None))
            .first()
        )
        if game_record:
            return game_record

        game_record = GameModel(
            code=game.code,
            game_type_id=self.get_game_type_id(game.game_type),
            start_dt=datetime.datetime.now(),
        )
        self.db.add(game_record)
        self.db.flush()
        return game_record

    def _get_or_create_users(self, players):
        chat_keys = {self._chat_key(player.user_id) for player in players}
        existing_users = self.db.query(User).filter(User.chat_id.in_(chat_keys)).all()
        users_by_chat_key = {self._chat_key(user.chat_id): user for user in existing_users}

        for player in players:
            chat_key = self._chat_key(player.user_id)
            if chat_key in users_by_chat_key:
                continue
            user = User(chat_id=chat_key, name=player.name)
            self.db.add(user)
            self.db.flush()
            users_by_chat_key[chat_key] = user

        return users_by_chat_key

    def _ensure_players(self, game_id: int, players, users_by_chat_key):
        user_ids = [users_by_chat_key[self._chat_key(player.user_id)].id for player in players]
        if user_ids:
            existing_records = (
                self.db.query(Player)
                .filter(Player.game_id == game_id, Player.user_id.in_(user_ids))
                .all()
            )
            existing_user_ids = {record.user_id for record in existing_records}
        else:
            existing_user_ids = set()

        for player in players:
            user_record = users_by_chat_key[self._chat_key(player.user_id)]
            if user_record.id in existing_user_ids:
                continue
            self.db.add(
                Player(
                    game_id=game_id,
                    user_id=user_record.id,
                    is_captain=player.is_captain,
                )
            )

    def _ensure_rounds(self, game_id: int, current_round: int):
        rounds_by_num = {
            round_record.num: round_record
            for round_record in self.db.query(Round).filter(Round.game_id == game_id).all()
        }
        for round_num in range(1, current_round + 1):
            if round_num in rounds_by_num:
                continue
            round_record = Round(game_id=game_id, num=round_num)
            self.db.add(round_record)
            self.db.flush()
            rounds_by_num[round_num] = round_record
        return rounds_by_num

    def _ensure_round_info(self, game_id: int, rounds_by_num, round_info_entries):
        round_numbers = {entry.round_id for entry in round_info_entries}
        missing_rounds = [num for num in round_numbers if num not in rounds_by_num]
        for round_num in missing_rounds:
            round_record = Round(game_id=game_id, num=round_num)
            self.db.add(round_record)
            self.db.flush()
            rounds_by_num[round_num] = round_record

        round_ids = [round_record.id for round_record in rounds_by_num.values()]
        existing_info = self.db.query(RoundInfo).filter(RoundInfo.round_id.in_(round_ids)).all() if round_ids else []
        existing_pairs = {(record.round_id, record.key) for record in existing_info}

        for entry in round_info_entries:
            round_record = rounds_by_num[entry.round_id]
            pair = (round_record.id, entry.key)
            if pair in existing_pairs:
                continue
            self.db.add(
                RoundInfo(
                    round_id=round_record.id,
                    key=entry.key,
                    value=entry.value,
                )
            )
            existing_pairs.add(pair)
