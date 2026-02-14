import random

from ...base_game import GameSession
from ...types import RoundInfoEntry
from . import texts


class MafiaGame(GameSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mafia_count: int | None = None
        self.civilian_count: int | None = None
        self.has_sheriff = False
        self.has_doctor = False
        self.setup_step: str | None = None

    def start_setup(self) -> str:
        self.mafia_count = None
        self.civilian_count = None
        self.has_sheriff = False
        self.has_doctor = False
        self.setup_step = "mafia_count"
        return f"{texts.SETUP_STARTED}\n{texts.PROMPT_MAFIA_COUNT}"

    def apply_setup_input(self, raw_text: str) -> str:
        if self.setup_step is None:
            return texts.SETUP_NOT_STARTED

        text = (raw_text or "").strip().lower()

        if self.setup_step == "mafia_count":
            count = self._parse_positive_int(text)
            if count is None:
                return f"{texts.SETUP_VALUE_ERROR_NUMBER}\n{texts.PROMPT_MAFIA_COUNT}"
            self.mafia_count = count
            self.setup_step = "civilian_count"
            return texts.PROMPT_CIVILIAN_COUNT

        if self.setup_step == "civilian_count":
            count = self._parse_positive_int(text)
            if count is None:
                return f"{texts.SETUP_VALUE_ERROR_NUMBER}\n{texts.PROMPT_CIVILIAN_COUNT}"
            self.civilian_count = count
            self.setup_step = "has_sheriff"
            return texts.PROMPT_HAS_SHERIFF

        if self.setup_step == "has_sheriff":
            value = self._parse_yes_no(text)
            if value is None:
                return f"{texts.SETUP_VALUE_ERROR_BOOL}\n{texts.PROMPT_HAS_SHERIFF}"
            self.has_sheriff = value
            self.setup_step = "has_doctor"
            return texts.PROMPT_HAS_DOCTOR

        if self.setup_step == "has_doctor":
            value = self._parse_yes_no(text)
            if value is None:
                return f"{texts.SETUP_VALUE_ERROR_BOOL}\n{texts.PROMPT_HAS_DOCTOR}"
            self.has_doctor = value
            self.setup_step = "done"
            return texts.SETUP_COMPLETED_TEMPLATE.format(
                mafia=self.mafia_count,
                civilian=self.civilian_count,
                sheriff="да" if self.has_sheriff else "нет",
                doctor="да" if self.has_doctor else "нет",
            )

        return texts.SETUP_NOT_STARTED

    def validate_before_deal(self) -> tuple[bool, str | None]:
        if self.setup_step != "done":
            return False, texts.SETUP_NOT_STARTED

        expected = self.expected_non_captain_players()
        actual = len(self._participants())
        if actual != expected:
            restart_prompt = self.start_setup().split("\n", 1)[1]
            return (
                False,
                texts.PLAYERS_COUNT_MISMATCH_TEMPLATE.format(
                    expected=expected,
                    actual=actual,
                    first_prompt=restart_prompt,
                ),
            )

        return True, None

    def deal_cards(self) -> list[tuple[int, str]]:
        ok, _ = self.validate_before_deal()
        if not ok:
            return []

        self.round += 1
        roles = self._build_roles_pool()
        participants = self._participants()
        random.shuffle(roles)
        random.shuffle(participants)

        messages: list[tuple[int, str]] = []
        for player, role in zip(participants, roles):
            self.round_info.append(
                RoundInfoEntry(
                    round_id=self.round,
                    key=f"mafia_role:{player.user_id}",
                    value=role,
                )
            )
            messages.append((player.user_id, texts.DEAL_TEMPLATE.format(role=role)))

        return messages

    def play(self):
        return []

    def get_rules(self):
        return texts.RULES_TEXT

    def expected_non_captain_players(self) -> int:
        return (
            int(self.mafia_count or 0)
            + int(self.civilian_count or 0)
            + (1 if self.has_sheriff else 0)
            + (1 if self.has_doctor else 0)
        )

    def _participants(self):
        return [player for player in self.players if player.user_id != self.captain_id]

    def _build_roles_pool(self) -> list[str]:
        roles = [texts.ROLE_MAFIA] * int(self.mafia_count or 0)
        roles += [texts.ROLE_CIVILIAN] * int(self.civilian_count or 0)
        if self.has_sheriff:
            roles.append(texts.ROLE_SHERIFF)
        if self.has_doctor:
            roles.append(texts.ROLE_DOCTOR)
        return roles

    @staticmethod
    def _parse_positive_int(text: str) -> int | None:
        try:
            value = int(text)
        except Exception:
            return None
        return value if value > 0 else None

    @staticmethod
    def _parse_yes_no(text: str) -> bool | None:
        yes_values = {"да", "yes", "y", "д"}
        no_values = {"нет", "no", "n", "н"}
        if text in yes_values:
            return True
        if text in no_values:
            return False
        return None
