import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from bot import texts
from bot.conversation import BotConversation
from bot.keyboards import build_markups


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
        self.game_manager.get_available_game_types.return_value = {"chameleon": "Заяц"}
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


if __name__ == "__main__":
    unittest.main()
