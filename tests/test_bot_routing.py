import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from bot import texts
from bot.conversation import BotConversation
from bot.keyboards import build_markups
from game.core.results import GameResult


def make_update(message_text: str, chat_id: int = 1, first_name: str = "User"):
    message = SimpleNamespace(
        text=message_text,
        chat_id=chat_id,
        from_user=SimpleNamespace(first_name=first_name),
    )
    message.reply_text = AsyncMock()
    return SimpleNamespace(message=message)


class BotRoutingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.game_manager = Mock()
        self.game_manager.get_available_game_types.return_value = {
            "chameleon": "Заяц",
            "mafia": "Мафия",
        }
        self.game_manager.submit_word.return_value = None
        self.game_manager.get_game_type_by_chat.return_value = None
        self.game_manager.play = AsyncMock(return_value=None)
        self.game_manager.start_whoami_round = AsyncMock(return_value=None)
        self.game_manager.start_mafia_setup = AsyncMock(return_value="Сколько будет мафии? Введите число.")
        self.game_manager.submit_mafia_setup = AsyncMock(return_value="ok")
        self.conversation = BotConversation(self.game_manager, build_markups())

    async def test_handle_message_unknown_command(self):
        update = make_update("unknown")
        context = SimpleNamespace(user_data={})

        await self.conversation.handle_message(update, context)

        update.message.reply_text.assert_awaited_once_with(texts.MSG_UNKNOWN_COMMAND)

    async def test_handle_message_routes_to_join_when_awaiting_code(self):
        update = make_update("1234")
        context = SimpleNamespace(user_data={"awaiting_code": True})
        self.conversation.join_game = AsyncMock()

        await self.conversation.handle_message(update, context)

        self.conversation.join_game.assert_awaited_once_with(update, context, "1234")

    async def test_handle_message_routes_to_create_game_by_alias(self):
        update = make_update("Заяц")
        context = SimpleNamespace(user_data={})
        self.conversation.create_game = AsyncMock()

        await self.conversation.handle_message(update, context)

        self.conversation.create_game.assert_awaited_once_with(update, context, "Заяц")

    async def test_handle_message_routes_to_command_handler(self):
        update = make_update(texts.CMD_RULES)
        context = SimpleNamespace(user_data={})
        handler = AsyncMock()
        self.conversation.command_handlers[texts.CMD_RULES] = handler

        await self.conversation.handle_message(update, context)

        handler.assert_awaited_once_with(update, context)

    async def test_handle_message_routes_to_submit_word(self):
        self.game_manager.submit_word.return_value = "Слово принято."
        update = make_update("Гэндальф")
        context = SimpleNamespace(user_data={})

        await self.conversation.handle_message(update, context)

        self.game_manager.submit_word.assert_called_once()
        update.message.reply_text.assert_awaited_once_with("Слово принято.")

    async def test_play_game_uses_start_whoami_round_for_whoami(self):
        self.game_manager.get_game_type_by_chat.return_value = "whoami"
        update = make_update("x", chat_id=7)
        context = SimpleNamespace(user_data={})

        await self.conversation.play_game(update, context)

        self.game_manager.start_whoami_round.assert_awaited_once_with(7)
        self.game_manager.play.assert_not_called()

    async def test_play_game_starts_mafia_setup_and_marks_waiting_state(self):
        self.game_manager.get_game_type_by_chat.return_value = "mafia"
        update = make_update("x", chat_id=7)
        context = SimpleNamespace(user_data={})

        await self.conversation.play_game(update, context)

        self.game_manager.start_mafia_setup.assert_awaited_once_with(7)
        self.assertTrue(context.user_data.get("awaiting_mafia_setup"))

    async def test_handle_message_routes_to_mafia_setup_input_when_waiting(self):
        update = make_update("2", chat_id=7)
        context = SimpleNamespace(user_data={"awaiting_mafia_setup": True})
        self.conversation.submit_mafia_setup = AsyncMock()

        await self.conversation.handle_message(update, context)

        self.conversation.submit_mafia_setup.assert_awaited_once_with(update, context, "2")

    async def test_play_game_returns_to_main_menu_for_not_found(self):
        self.game_manager.get_game_type_by_chat.return_value = "whoami"
        self.game_manager.start_whoami_round.return_value = GameResult.GAME_NOT_FOUND
        self.conversation.return_to_main_menu = AsyncMock()
        update = make_update("x", chat_id=7)
        context = SimpleNamespace(user_data={})

        await self.conversation.play_game(update, context)

        self.conversation.return_to_main_menu.assert_awaited_once_with(update, context)


if __name__ == "__main__":
    unittest.main()
