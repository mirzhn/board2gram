from . import texts


def build_command_handlers(conversation):
    return {
        texts.CMD_CREATE_GAME: conversation.show_game_types,
        texts.CMD_JOIN_GAME: conversation.await_game_code,
        texts.CMD_START_GAME: conversation.play_game,
        texts.CMD_NEXT_ROUND: conversation.play_game,
        texts.CMD_DEAL_CARDS: conversation.deal_cards,
        texts.CMD_STOP_GAME: conversation.stop_game,
        texts.CMD_RULES: conversation.show_game_rules,
        texts.CMD_LEAVE_GAME: conversation.leave_game,
    }
