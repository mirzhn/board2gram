import unittest

from game.mafia_game import MafiaGame


class MafiaGameTests(unittest.TestCase):
    def setUp(self):
        self.game = MafiaGame([], {"chat_id": 1, "name": "Captain"}, "3333", "mafia")
        self.game.join({"chat_id": 2, "name": "P2"})
        self.game.join({"chat_id": 3, "name": "P3"})
        self.game.join({"chat_id": 4, "name": "P4"})

    def test_setup_and_deal_excludes_captain(self):
        self.game.start_setup()
        self.game.apply_setup_input("1")
        self.game.apply_setup_input("1")
        self.game.apply_setup_input("да")
        done_message = self.game.apply_setup_input("нет")

        self.assertIn("Настройка сохранена", done_message)

        messages = self.game.deal_cards()

        self.assertEqual(len(messages), 3)
        self.assertNotIn(1, [chat_id for chat_id, _ in messages])
        self.assertEqual(self.game.round, 1)
        self.assertEqual(len(self.game.round_info), 3)

    def test_mismatch_restarts_setup(self):
        self.game.start_setup()
        self.game.apply_setup_input("2")
        self.game.apply_setup_input("2")
        self.game.apply_setup_input("да")
        self.game.apply_setup_input("да")

        ok, reason = self.game.validate_before_deal()

        self.assertFalse(ok)
        self.assertIn("Запускаем настройку заново", reason)
        self.assertIn("Сколько будет мафии", reason)
        self.assertEqual(self.game.setup_step, "mafia_count")

    def test_invalid_setup_input_returns_validation_error(self):
        self.game.start_setup()

        message = self.game.apply_setup_input("abc")

        self.assertIn("Нужно ввести целое число", message)
        self.assertIn("Сколько будет мафии", message)


if __name__ == "__main__":
    unittest.main()
