import random
import unittest

from game.mafia_game import MafiaGame
from game.whoami_game import WhoAmIGame


class GameSimulationTests(unittest.TestCase):
    def test_mafia_simulation_multi_round_deals(self):
        game = MafiaGame([], {"chat_id": 1, "name": "Captain"}, "9001", "mafia")
        for player_id in range(2, 8):
            game.join({"chat_id": player_id, "name": f"P{player_id}"})

        game.start_setup()
        game.apply_setup_input("2")
        game.apply_setup_input("2")
        game.apply_setup_input("да")
        game.apply_setup_input("да")

        role_counts = {player.user_id: {} for player in game.players if player.user_id != game.captain_id}
        rounds = 30

        for seed in range(1000, 1000 + rounds):
            random.seed(seed)
            messages = game.deal_cards()

            self.assertEqual(len(messages), 6)
            recipient_ids = {chat_id for chat_id, _ in messages}
            self.assertNotIn(game.captain_id, recipient_ids)

            round_roles = [text.split(": ", 1)[1] for _, text in messages]
            self.assertEqual(round_roles.count("мафия"), 2)
            self.assertEqual(round_roles.count("мирный"), 2)
            self.assertEqual(round_roles.count("шериф"), 1)
            self.assertEqual(round_roles.count("доктор"), 1)

            for chat_id, text in messages:
                role = text.split(": ", 1)[1]
                role_counts[chat_id][role] = role_counts[chat_id].get(role, 0) + 1

        for player_stats in role_counts.values():
            self.assertGreater(len(player_stats), 1)

    def test_whoami_simulation_no_self_assignment(self):
        game = WhoAmIGame([], {"chat_id": 1, "name": "P1"}, "9002", "whoami")
        for player_id in range(2, 7):
            game.join({"chat_id": player_id, "name": f"P{player_id}"})

        rounds = 30
        for round_num in range(1, rounds + 1):
            game.start_round()

            submitted_words = {}
            for player in game.players:
                word = f"W{round_num}_{player.user_id}"
                submitted_words[player.user_id] = word
                game.submit_word(player.user_id, word)

            messages = game.deal_cards()
            self.assertEqual(len(messages), len(game.players))

            round_info = [
                entry
                for entry in game.round_info
                if entry.round_id == game.round and entry.key.startswith("whoami:")
            ]
            self.assertEqual(len(round_info), len(game.players))

            assigned_words = set()
            for entry in round_info:
                receiver_id = int(entry.key.split(":", 1)[1])
                assigned_word = str(entry.value)
                assigned_words.add(assigned_word)
                self.assertNotEqual(assigned_word, submitted_words[receiver_id])

            self.assertEqual(assigned_words, set(submitted_words.values()))


if __name__ == "__main__":
    unittest.main()
