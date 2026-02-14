import random

from ...base_game import GameSession
from ...types import RoundInfoEntry
from . import texts


class WhoAmIGame(GameSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submitted_words: dict[int, str] = {}

    def submit_word(self, user_id: int, word: str) -> str:
        clean_word = word.strip()
        if not clean_word:
            return texts.WORD_REJECTED_EMPTY

        existed = user_id in self.submitted_words
        self.submitted_words[user_id] = clean_word
        return texts.WORD_REPLACED if existed else texts.WORD_ACCEPTED

    def can_deal(self) -> bool:
        player_ids = [player.user_id for player in self.players]
        if len(player_ids) < 2:
            return False
        return len(self.submitted_words) == len(player_ids)

    def start_round(self) -> str:
        self.submitted_words = {}
        return texts.ROUND_STARTED

    def deal_cards(self) -> list[tuple[int, str]]:
        if not self.can_deal():
            return []

        self.round += 1
        assignments = self._build_derangement()
        round_messages = []

        for receiver_id, assigned_word in assignments.items():
            self.round_info.append(
                RoundInfoEntry(
                    round_id=self.round,
                    key=f"whoami:{receiver_id}",
                    value=assigned_word,
                )
            )

        for recipient in self.players:
            rows = []
            for player in self.players:
                if player.user_id == recipient.user_id:
                    continue
                rows.append(f"{player.name}: {assignments[player.user_id]}")
            message = texts.DEAL_RESULT_TEMPLATE.format(
                round_num=self.round,
                rows="\n".join(rows) if rows else "Нет данных.",
            )
            round_messages.append((recipient.user_id, message))

        self.submitted_words = {}
        return round_messages

    def get_missing_players(self) -> list[str]:
        submitted = set(self.submitted_words)
        return [player.name for player in self.players if player.user_id not in submitted]

    def waiting_message(self) -> str:
        missing_players = self.get_missing_players()
        return texts.WAITING_FOR_WORDS_TEMPLATE.format(
            submitted=len(self.submitted_words),
            total=len(self.players),
            missing_players=", ".join(missing_players) if missing_players else "-",
        )

    def play(self):
        return self.deal_cards()

    def get_rules(self):
        return texts.RULES_TEXT

    def _build_derangement(self) -> dict[int, str]:
        player_ids = [player.user_id for player in self.players]
        words_by_author = {player_id: self.submitted_words[player_id] for player_id in player_ids}
        candidates = player_ids[:]

        while True:
            random.shuffle(candidates)
            if all(receiver != source for receiver, source in zip(player_ids, candidates)):
                break

        return {receiver: words_by_author[source] for receiver, source in zip(player_ids, candidates)}
