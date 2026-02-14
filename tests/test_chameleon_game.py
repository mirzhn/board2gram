import unittest

from game.chameleon_game import ChameleonGame


def make_deck():
    return [
        {
            "id": 1,
            "key": "topic",
            "value": '{"topic": "Animals", "words": ["Cat", "Dog", "Fox", "Bear"]}',
        }
    ]


class ChameleonGameTests(unittest.TestCase):
    def setUp(self):
        captain = {"chat_id": 1, "name": "P1"}
        self.game = ChameleonGame(make_deck(), captain, "1234", "chameleon")
        self.game.join({"chat_id": 2, "name": "P2"})
        self.game.join({"chat_id": 3, "name": "P3"})
        self.game.join({"chat_id": 4, "name": "P4"})

    def test_assign_roles_sets_exactly_one_chameleon(self):
        self.game.assign_roles()
        chameleons = [p for p in self.game.players if p["role"] == "chameleon"]
        self.assertEqual(len(chameleons), 1)

    def test_join_does_not_duplicate_same_player(self):
        before = len(self.game.players)
        self.game.join({"chat_id": 2, "name": "P2"})
        after = len(self.game.players)
        self.assertEqual(before, after)

    def test_chameleon_selection_is_statistically_balanced(self):
        rounds = 20000
        counts = {p["user_id"]: 0 for p in self.game.players}

        for _ in range(rounds):
            chosen = self.game.assign_roles()
            counts[chosen["user_id"]] += 1

        expected = rounds / len(self.game.players)
        tolerance = expected * 0.10
        for value in counts.values():
            self.assertLessEqual(abs(value - expected), tolerance)

    def test_chameleon_report_for_6_players(self):
        rounds = 30
        captain = {"chat_id": 1, "name": "P1"}
        game = ChameleonGame(make_deck(), captain, "9999", "chameleon")
        for player_id in range(2, 7):
            game.join({"chat_id": player_id, "name": f"P{player_id}"})

        counts = {p["user_id"]: 0 for p in game.players}
        max_streak = {p["user_id"]: 0 for p in game.players}
        streak_runs = {p["user_id"]: 0 for p in game.players}

        previous = None
        current_streak = 0

        for _ in range(rounds):
            chosen = game.assign_roles()["user_id"]
            counts[chosen] += 1

            if chosen == previous:
                current_streak += 1
            else:
                if previous is not None and current_streak >= 2:
                    streak_runs[previous] += 1
                previous = chosen
                current_streak = 1

            if current_streak > max_streak[chosen]:
                max_streak[chosen] = current_streak

        if previous is not None and current_streak >= 2:
            streak_runs[previous] += 1

        lines = ["6-player chameleon random report:"]
        for user_id in sorted(counts):
            lines.append(
                f"player {user_id}: total={counts[user_id]}, "
                f"max_streak={max_streak[user_id]}, streak_runs={streak_runs[user_id]}"
            )
        print("\n" + "\n".join(lines))

        self.assertEqual(len(game.players), 6)
        self.assertEqual(sum(counts.values()), rounds)


if __name__ == "__main__":
    unittest.main()
