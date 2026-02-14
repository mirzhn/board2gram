import unittest

from game.ilito_game import IlitoGame


def make_ilito_deck():
    return [
        {"id": 1, "key": "pair", "value": '{"left":"Кофе","right":"Чай"}'},
        {"id": 2, "key": "pair", "value": "Горы | Море"},
    ]


class IlitoGameTests(unittest.TestCase):
    def setUp(self):
        captain = {"chat_id": 1, "name": "P1"}
        self.game = IlitoGame(make_ilito_deck(), captain, "5555", "ilito")
        self.game.join({"chat_id": 2, "name": "P2"})
        self.game.join({"chat_id": 3, "name": "P3"})

    def test_play_sends_one_card_to_all_players(self):
        messages = self.game.play()

        self.assertEqual(self.game.round, 1)
        self.assertEqual(len(messages), len(self.game.players))
        self.assertTrue(all("Раунд 1" in text for _, text in messages))
        self.assertTrue(all("A:" in text and "B:" in text for _, text in messages))

        round_info = [entry for entry in self.game.round_info if entry.key == "ilito_card"]
        self.assertEqual(len(round_info), 1)
        self.assertEqual(round_info[0].round_id, 1)

    def test_rules_are_available(self):
        rules = self.game.get_rules()
        self.assertIn("Илито", rules)
        self.assertIn("Следующий раунд", rules)


if __name__ == "__main__":
    unittest.main()
