import json

from ...base_game import GameSession
from ...types import RoundInfoEntry
from .texts import ROUND_MESSAGE_TEMPLATE, RULES_TEXT


class IlitoGame(GameSession):
    def play(self):
        self.round += 1
        card = self.get_random_card()
        left, right = self._parse_card_value(card.value)
        message = ROUND_MESSAGE_TEMPLATE.format(
            round_num=self.round,
            left=left,
            right=right,
        )

        self.round_info.append(RoundInfoEntry(round_id=self.round, key="ilito_card", value=card.id))
        return [(player.user_id, message) for player in self.players]

    def get_rules(self):
        return RULES_TEXT

    def _parse_card_value(self, value: str) -> tuple[str, str]:
        # Prefer JSON payload but support simple "A|B" fallback.
        try:
            payload = json.loads(value)
            if isinstance(payload, dict):
                left = str(payload.get("left", "")).strip()
                right = str(payload.get("right", "")).strip()
                if left and right:
                    return left, right
        except Exception:
            pass

        if "|" in value:
            left, right = value.split("|", 1)
            return left.strip(), right.strip()

        return value.strip(), "—"
