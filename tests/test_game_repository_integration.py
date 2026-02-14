import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from game.base_game import GameSession
from game.core.repository import GameRepository
from game.types import RoundInfoEntry
from models import Base, Game as GameModel, GameType, GameTypeCard, Player, Round, RoundInfo, User


def seed_game_type_with_deck(session, game_type_name: str):
    game_type = GameType(name=game_type_name)
    session.add(game_type)
    session.flush()

    session.add_all(
        [
            GameTypeCard(
                game_type_id=game_type.id,
                key="topic",
                value='{"topic":"Animals","words":["Cat","Dog","Fox","Bear"]}',
            ),
            GameTypeCard(
                game_type_id=game_type.id,
                key="topic",
                value='{"topic":"Food","words":["Soup","Rice","Bread","Tea"]}',
            ),
        ]
    )
    session.commit()


class GameRepositoryIntegrationTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        seed_game_type_with_deck(self.session, "chameleon")
        self.repository = GameRepository(self.session)

    def tearDown(self):
        self.session.close()

    def _make_game(self):
        deck = self.repository.get_deck("chameleon")
        game = GameSession(
            deck=deck,
            user={"chat_id": 1001, "name": "Captain"},
            code="7777",
            game_type="chameleon",
        )
        game.join({"chat_id": 1002, "name": "Player2"})
        game.round = 2
        game.round_info = [
            RoundInfoEntry(round_id=1, key="chameleon", value=1002),
            RoundInfoEntry(round_id=1, key="card", value=1),
            RoundInfoEntry(round_id=2, key="chameleon", value=1001),
        ]
        return game

    def test_save_then_load_then_stop(self):
        game = self._make_game()

        self.repository.save(game)
        loaded = self.repository.load("7777")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.code, "7777")
        self.assertEqual(loaded.game_type, "chameleon")
        self.assertEqual(loaded.round, 2)
        self.assertEqual(len(loaded.players), 2)
        self.assertEqual({p.user_id for p in loaded.players}, {1001, 1002})
        self.assertGreaterEqual(len(loaded.round_info), 3)

        open_codes = self.repository.get_open_game_codes()
        self.assertIn("7777", open_codes)

        self.repository.stop(game)
        self.assertIsNone(self.repository.load("7777"))
        self.assertNotIn("7777", self.repository.get_open_game_codes())

    def test_save_is_idempotent_for_players_rounds_and_round_info(self):
        game = self._make_game()

        self.repository.save(game)
        self.repository.save(game)

        game_record = self.session.query(GameModel).filter(GameModel.code == "7777").one()
        users = self.session.query(User).all()
        players = self.session.query(Player).filter(Player.game_id == game_record.id).all()
        rounds = self.session.query(Round).filter(Round.game_id == game_record.id).all()
        round_info = (
            self.session.query(RoundInfo)
            .join(Round, RoundInfo.round_id == Round.id)
            .filter(Round.game_id == game_record.id)
            .all()
        )

        self.assertEqual(len(users), 2)
        self.assertEqual(len(players), 2)
        self.assertEqual(len(rounds), 2)
        self.assertEqual(len(round_info), 3)


if __name__ == "__main__":
    unittest.main()
