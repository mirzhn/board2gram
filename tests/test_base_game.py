import unittest

from game.base_game import GameSession


class DummyGame(GameSession):
    def play(self):
        return []


def make_deck():
    return [
        {"id": 1, "key": "a", "value": "A1"},
        {"id": 2, "key": "a", "value": "A2"},
        {"id": 3, "key": "b", "value": "B1"},
    ]


class BaseGameTests(unittest.TestCase):
    def setUp(self):
        captain = {"chat_id": 1, "name": "P1"}
        self.game = DummyGame(make_deck(), captain, "1234", "dummy")

    def test_join_and_prevent_duplicate(self):
        self.game.join({"chat_id": 2, "name": "P2"})
        self.game.join({"chat_id": 2, "name": "P2"})
        ids = [player.user_id for player in self.game.players]
        self.assertEqual(ids.count(2), 1)

    def test_leave_removes_player(self):
        self.game.join({"chat_id": 2, "name": "P2"})
        self.game.leave({"chat_id": 2, "name": "P2"})
        ids = [player.user_id for player in self.game.players]
        self.assertNotIn(2, ids)

    def test_get_random_card_by_category(self):
        card = self.game.get_random_card("b")
        self.assertEqual(card.key, "b")
        self.assertIn(card, self.game.used_deck)


if __name__ == "__main__":
    unittest.main()
