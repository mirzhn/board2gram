import random

from .types import Card, PlayerState, RoundInfoEntry, UserPayload


class GameSession:
    def __init__(
        self,
        deck: list[Card],
        user: UserPayload,
        code: str,
        game_type: str,
        players: list[PlayerState] | None = None,
        round: int = 0,
    ):
        self.deck = [Card.from_any(card) for card in deck]
        self.used_deck: list[Card] = []
        self.code = code
        self.game_type = game_type
        self.players = [PlayerState.from_any(player) for player in (players or [])]
        self.round = round
        self.round_info: list[RoundInfoEntry] = []

        user_payload = UserPayload.from_any(user)
        self.join(user_payload, True)
        self.captain_id = user_payload.chat_id
        self.rules = ""

    def join(self, user: UserPayload, is_captain: bool = False):
        user_payload = UserPayload.from_any(user)
        if any(player.user_id == user_payload.chat_id for player in self.players):
            return
        self.players.append(
            PlayerState(
                user_id=user_payload.chat_id,
                name=user_payload.name,
                role="player",
                is_captain=is_captain,
            )
        )

    def leave(self, user: UserPayload):
        user_payload = UserPayload.from_any(user)
        self.players = [player for player in self.players if player.user_id != user_payload.chat_id]

    def play(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_random_card(self, category_key: str | None = None) -> Card:
        self.deck = [card for card in self.deck if card not in self.used_deck]

        if category_key:
            filtered_deck = [card for card in self.deck if card.key == category_key]
        else:
            filtered_deck = self.deck

        selected_card = random.choice(filtered_deck)
        self.used_deck.append(selected_card)
        return selected_card

    def get_rules(self):
        return self.rules
