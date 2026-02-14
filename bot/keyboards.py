from dataclasses import dataclass

from telegram import ReplyKeyboardMarkup

from . import texts


@dataclass
class BotMarkups:
    main_menu: ReplyKeyboardMarkup
    in_game_captain: ReplyKeyboardMarkup
    in_game_player: ReplyKeyboardMarkup


def build_markups() -> BotMarkups:
    return BotMarkups(
        main_menu=ReplyKeyboardMarkup(
            texts.MAIN_MENU_KEYBOARD,
            one_time_keyboard=False,
            resize_keyboard=True,
        ),
        in_game_captain=ReplyKeyboardMarkup(
            texts.IN_GAME_CAPTAIN_KEYBOARD,
            one_time_keyboard=False,
            resize_keyboard=True,
        ),
        in_game_player=ReplyKeyboardMarkup(
            texts.IN_GAME_PLAYER_KEYBOARD,
            one_time_keyboard=False,
            resize_keyboard=True,
        ),
    )
