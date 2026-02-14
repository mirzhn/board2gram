from dataclasses import dataclass

from telegram import ReplyKeyboardMarkup

from . import texts


@dataclass
class BotMarkups:
    main_menu: ReplyKeyboardMarkup
    in_game_captain: ReplyKeyboardMarkup
    in_game_player: ReplyKeyboardMarkup
    captain_by_game_type: dict[str, ReplyKeyboardMarkup]

    def get_captain_markup(self, game_type: str) -> ReplyKeyboardMarkup:
        return self.captain_by_game_type.get(game_type, self.in_game_captain)

    def get_player_markup(self, game_type: str) -> ReplyKeyboardMarkup:
        _ = game_type
        return self.in_game_player


def _keyboard(layout):
    return ReplyKeyboardMarkup(layout, one_time_keyboard=False, resize_keyboard=True)


def build_markups() -> BotMarkups:
    captain_default = _keyboard(texts.IN_GAME_CAPTAIN_KEYBOARD_DEFAULT)
    return BotMarkups(
        main_menu=_keyboard(texts.MAIN_MENU_KEYBOARD),
        in_game_captain=captain_default,
        in_game_player=_keyboard(texts.IN_GAME_PLAYER_KEYBOARD),
        captain_by_game_type={
            "chameleon": captain_default,
            "bunker": captain_default,
            "ilito": captain_default,
            "whoami": _keyboard(texts.IN_GAME_CAPTAIN_KEYBOARD_WHOAMI),
            "mafia": _keyboard(texts.IN_GAME_CAPTAIN_KEYBOARD_MAFIA),
        },
    )
