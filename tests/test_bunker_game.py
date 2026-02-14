import unittest

from game.bunker_game import BunkerGame


def make_bunker_deck():
    deck = []
    card_id = 1

    for key, count in [
        ("reason", 3),
        ("bunker", 3),
        ("hobby", 6),
        ("health", 6),
        ("biology", 6),
        ("baggage", 6),
        ("fact", 6),
        ("career", 6),
    ]:
        for i in range(1, count + 1):
            deck.append({"id": card_id, "key": key, "value": f"{key}_{i}"})
            card_id += 1
    return deck


class BunkerGameTests(unittest.TestCase):
    def setUp(self):
        captain = {"chat_id": 1, "name": "P1"}
        self.game = BunkerGame(make_bunker_deck(), captain, "4321", "bunker")
        self.game.join({"chat_id": 2, "name": "P2"})
        self.game.join({"chat_id": 3, "name": "P3"})

    def test_first_round_sends_reason_and_profiles(self):
        messages = self.game.play()

        self.assertEqual(self.game.round, 1)
        self.assertEqual(len(messages), 1 + len(self.game.players))

        captain_chat_id, captain_message = messages[0]
        self.assertEqual(captain_chat_id, self.game.captain_id)
        self.assertIn("Причина конца света", captain_message)

        profile_messages = messages[1:]
        self.assertEqual(len(profile_messages), len(self.game.players))
        for _, text in profile_messages:
            self.assertIn("<b>хобби</b>", text)
            self.assertIn("<b>профессия</b>", text)

        bunker_round_info = [x for x in self.game.round_info if x.key == "bunker"]
        self.assertEqual(len(bunker_round_info), 0)

    def test_second_round_sends_bunker_fact_and_saves_round_info(self):
        self.game.play()
        messages = self.game.play()

        self.assertEqual(self.game.round, 2)
        self.assertEqual(len(messages), 1)

        chat_id, text = messages[0]
        self.assertEqual(chat_id, self.game.captain_id)
        self.assertIn("Факт о бункере", text)

        bunker_round_info = [x for x in self.game.round_info if x.key == "bunker"]
        self.assertEqual(len(bunker_round_info), 1)
        self.assertEqual(bunker_round_info[0].round_id, 2)

    def test_rules_are_available(self):
        rules = self.game.get_rules()
        self.assertIn("Игра БУНКЕР", rules)
        self.assertIn("Цель игры", rules)


if __name__ == "__main__":
    unittest.main()
