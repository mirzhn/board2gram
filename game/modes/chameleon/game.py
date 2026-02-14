import json
import random

from ...base_game import GameSession
from ...types import RoundInfoEntry
from .texts import CHAMELEON_SUFFIX, PLAYER_SUFFIX_TEMPLATE, ROUND_MESSAGE_TEMPLATE, RULES_TEXT


class ChameleonGame(GameSession):
    def play(self):
        self.round += 1
        messages = []
        chameleon = self.assign_roles()
        card = self.get_random_card()

        payload = json.loads(card.value)
        card_words = payload["words"]
        card_topic = payload["topic"]
        selected_word = random.choice(card_words)

        self.round_info.append(
            RoundInfoEntry(round_id=self.round, key="chameleon", value=chameleon.user_id)
        )
        self.round_info.append(RoundInfoEntry(round_id=self.round, key="card", value=card.id))
        self.round_info.append(
            RoundInfoEntry(round_id=self.round, key="selected_word", value=selected_word)
        )

        message = ROUND_MESSAGE_TEMPLATE.format(
            round_num=self.round,
            topic=card_topic,
            table=self.get_format_table(card_words),
        )
        for player in self.players:
            if player.role == "chameleon":
                messages.append((player.user_id, message + CHAMELEON_SUFFIX))
            else:
                messages.append(
                    (
                        player.user_id,
                        message + PLAYER_SUFFIX_TEMPLATE.format(selected_word=selected_word),
                    )
                )
        return messages

    def assign_roles(self):
        for player in self.players:
            player.role = "player"
        chameleon = random.choice(self.players)
        chameleon.role = "chameleon"
        return chameleon

    def get_format_table(self, words: list[str]) -> str:
        table_rows = []
        table_html = "<pre>\n"

        column_width = max(len(word) for word in words)
        for i in range(0, len(words), 2):
            table_rows.append(words[i : i + 2])

        for row in table_rows:
            table_html += "| " + " | ".join(f"{word:<{column_width}}" for word in row) + " |\n"

        table_html += "</pre>"
        return table_html

    def get_rules(self):
        return RULES_TEXT
