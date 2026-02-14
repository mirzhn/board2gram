import unittest

from game.game_factory import GameFactory


class DummyGame:
    def __init__(self, value):
        self.value = value


class GameFactoryTests(unittest.TestCase):
    def test_register_and_get_game(self):
        factory = GameFactory()
        factory.register_game("dummy", DummyGame, "Dummy")

        game = factory.get_game("dummy", 42)

        self.assertIsInstance(game, DummyGame)
        self.assertEqual(game.value, 42)

    def test_get_game_raises_for_unregistered_game(self):
        factory = GameFactory()
        with self.assertRaises(ValueError):
            factory.get_game("missing")

    def test_get_available_game_types(self):
        factory = GameFactory()
        factory.register_game("a", DummyGame, "A")
        factory.register_game("b", DummyGame, "B")

        aliases = factory.get_available_game_types()

        self.assertEqual(aliases["a"], "A")
        self.assertEqual(aliases["b"], "B")


if __name__ == "__main__":
    unittest.main()
