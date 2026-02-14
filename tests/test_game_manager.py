import unittest
from unittest.mock import AsyncMock, Mock

from game.game_manager import GameManager
from game.core.results import GameResult
from game.types import PlayerState, UserPayload


class StubGame:
    def __init__(self):
        self.code = "1234"
        self.game_type = "chameleon"
        self.captain_id = 1
        self.players = [
            PlayerState(user_id=1, name="P1", role="player", is_captain=True),
            PlayerState(user_id=2, name="P2", role="player", is_captain=False),
        ]
        self.join = Mock()
        self.leave = Mock()
        self.play = Mock(return_value=[(1, "m1"), (2, "m2")])
        self.get_rules = Mock(return_value="rules")


class GameManagerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.notifier = AsyncMock()
        self.manager = GameManager(db=None, notifier=self.notifier)
        self.manager.game_service = Mock()

    def test_generate_code_skips_existing(self):
        code = self.manager.generate_code({"1111", "2222"})
        self.assertEqual(len(code), 4)
        self.assertNotIn(code, {"1111", "2222"})

    def test_start_creates_and_tracks_game(self):
        user = {"chat_id": 10, "name": "U1"}
        game = StubGame()
        self.manager.game_service.get_open_game_codes.return_value = ["0001"]
        self.manager.game_service.get_deck.return_value = [{"id": 1}]
        self.manager.generate_code = Mock(return_value="9999")
        self.manager.create_game = Mock(return_value=game)

        code = self.manager.start(user, "chameleon")

        self.assertEqual(code, "9999")
        self.manager.create_game.assert_called_once()
        self.assertIs(self.manager.games_by_code["9999"], game)
        self.assertIs(self.manager.games_by_chat[10], game)

    async def test_join_existing_game(self):
        game = StubGame()
        self.manager.games_by_code["1234"] = game
        user = {"chat_id": 55, "name": "New"}

        message = await self.manager.join(user, "1234")

        game.join.assert_called_once()
        self.assertEqual(game.join.call_args.args[0], UserPayload(chat_id=55, name="New"))
        self.assertIs(self.manager.games_by_chat[55], game)
        self.notifier.notify.assert_awaited_with(game.captain_id, unittest.mock.ANY)
        self.assertIn("1234", message)

    async def test_join_missing_game(self):
        message = await self.manager.join({"chat_id": 55, "name": "New"}, "0000")
        self.assertEqual(message, GameResult.GAME_NOT_FOUND)

    async def test_play_existing_game(self):
        game = StubGame()
        self.manager.games_by_chat[1] = game

        message = await self.manager.play(1)

        self.assertIsNone(message)
        self.assertEqual(self.notifier.notify.await_count, 2)

    async def test_play_missing_game(self):
        message = await self.manager.play(404)
        self.assertEqual(message, GameResult.GAME_NOT_FOUND)

    async def test_stop_existing_game(self):
        game = StubGame()
        self.manager.games_by_chat[1] = game
        self.manager.save = Mock()

        message = await self.manager.stop(1)

        self.manager.save.assert_called_once_with(game)
        self.manager.game_service.stop.assert_called_once_with(game)
        self.assertNotIn(1, self.manager.games_by_chat)
        self.assertNotEqual(message, GameResult.GAME_NOT_FOUND)
        self.assertGreaterEqual(self.notifier.notify.await_count, 1)

    async def test_stop_missing_game(self):
        message = await self.manager.stop(404)
        self.assertEqual(message, GameResult.GAME_NOT_FOUND)

    def test_reload_tracks_loaded_game(self):
        game = StubGame()
        self.manager.game_service.reload.return_value = game

        loaded = self.manager.reload("1234")

        self.assertIs(loaded, game)
        self.assertIs(self.manager.games_by_code["1234"], game)

    def test_reload_returns_none_for_missing_game(self):
        self.manager.game_service.reload.return_value = None
        loaded = self.manager.reload("1234")
        self.assertIsNone(loaded)

    async def test_get_rules_existing_game(self):
        game = StubGame()
        self.manager.games_by_chat[1] = game

        rules = await self.manager.get_rules(1)

        self.assertEqual(rules, "rules")
        game.get_rules.assert_called_once()

    async def test_get_rules_missing_game(self):
        rules = await self.manager.get_rules(0)
        self.assertEqual(rules, GameResult.GAME_NOT_FOUND)

    async def test_leave_existing_game(self):
        game = StubGame()
        self.manager.games_by_chat[2] = game
        user = {"chat_id": 2, "name": "P2"}

        message = await self.manager.leave(user)

        game.leave.assert_called_once()
        self.assertEqual(game.leave.call_args.args[0], UserPayload(chat_id=2, name="P2"))
        self.assertNotEqual(message, GameResult.GAME_NOT_FOUND)
        self.notifier.notify.assert_awaited_with(game.captain_id, unittest.mock.ANY)

    async def test_leave_missing_game(self):
        message = await self.manager.leave({"chat_id": 2, "name": "P2"})
        self.assertEqual(message, GameResult.GAME_NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
