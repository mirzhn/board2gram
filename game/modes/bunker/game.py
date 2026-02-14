from ...base_game import GameSession
from ...types import RoundInfoEntry
from .texts import BUNKER_FACT_PREFIX, PLAYER_INFO_TEMPLATE, REASON_PREFIX, RULES_TEXT


class BunkerGame(GameSession):
    def play(self):
        self.round += 1
        messages = []

        if self.round == 1:
            reason_card = self.get_random_card("reason")
            messages.append((self.captain_id, REASON_PREFIX + reason_card.value))
            for player in self.players:
                messages.append((player.user_id, self.get_player_info()))
        else:
            bunker_card = self.get_random_card("bunker")
            messages.append((self.captain_id, BUNKER_FACT_PREFIX + bunker_card.value))
            self.round_info.append(
                RoundInfoEntry(round_id=self.round, key="bunker", value=bunker_card.id)
            )

        return messages

    def get_player_info(self):
        return PLAYER_INFO_TEMPLATE.format(
            hobby=self.get_random_card("hobby").value,
            health=self.get_random_card("health").value,
            biology=self.get_random_card("biology").value,
            baggage=self.get_random_card("baggage").value,
            fact=self.get_random_card("fact").value,
            career=self.get_random_card("career").value,
        )

    def get_rules(self):
        return RULES_TEXT
