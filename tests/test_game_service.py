import unittest
from unittest.mock import Mock, patch

from game.core.service import GameService


class GameServiceTests(unittest.TestCase):
    @patch("game.core.service.GameRepository")
    def test_delegates_calls_to_repository(self, repository_cls):
        repository = Mock()
        repository_cls.return_value = repository
        repository.get_open_game_codes.return_value = ["1111", "2222"]
        repository.get_deck.return_value = [{"id": 1}]
        repository.load.return_value = object()

        service = GameService(db=object())
        game = object()

        codes = service.get_open_game_codes()
        deck = service.get_deck("chameleon")
        service.save(game)
        loaded = service.reload("1111")
        service.stop(game)

        self.assertEqual(codes, ["1111", "2222"])
        self.assertEqual(deck, [{"id": 1}])
        self.assertIsNotNone(loaded)
        repository.get_open_game_codes.assert_called_once()
        repository.get_deck.assert_called_once_with("chameleon")
        repository.save.assert_called_once_with(game)
        repository.load.assert_called_once_with("1111")
        repository.stop.assert_called_once_with(game)


if __name__ == "__main__":
    unittest.main()
