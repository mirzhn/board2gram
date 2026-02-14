import unittest

from game.whoami_game import WhoAmIGame


def make_deck():
    return [{"id": 1, "key": "pair", "value": '{"left":"A","right":"B"}'}]


class WhoAmIGameTests(unittest.TestCase):
    def setUp(self):
        self.game = WhoAmIGame(make_deck(), {"chat_id": 1, "name": "P1"}, "0001", "whoami")
        self.game.join({"chat_id": 2, "name": "P2"})
        self.game.join({"chat_id": 3, "name": "P3"})

    def test_deal_requires_words_from_all_players(self):
        self.game.submit_word(1, "A")
        self.game.submit_word(2, "B")
        self.assertFalse(self.game.can_deal())
        waiting = self.game.waiting_message()
        self.assertIn("Сдано: 2/3", waiting)
        self.assertIn("P3", waiting)

    def test_start_round_resets_submitted_words(self):
        self.game.submit_word(1, "A")
        self.game.submit_word(2, "B")

        message = self.game.start_round()

        self.assertEqual(self.game.submitted_words, {})
        self.assertIn("Новый раунд", message)

    def test_deal_assigns_without_self_and_hides_self_row(self):
        self.game.submit_word(1, "Лев")
        self.game.submit_word(2, "Тигр")
        self.game.submit_word(3, "Медведь")

        messages = self.game.deal_cards()

        self.assertEqual(self.game.round, 1)
        self.assertEqual(len(messages), 3)
        for chat_id, text in messages:
            own_name = next(player.name for player in self.game.players if player.user_id == chat_id)
            self.assertNotIn(f"{own_name}:", text)
            self.assertIn("Раунд 1", text)

        self.assertEqual(len([x for x in self.game.round_info if x.key.startswith("whoami:")]), 3)


if __name__ == "__main__":
    unittest.main()
