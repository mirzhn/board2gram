from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Card:
    id: int
    key: str
    value: str

    @classmethod
    def from_any(cls, raw: Any) -> "Card":
        if isinstance(raw, cls):
            return raw
        if isinstance(raw, Mapping):
            return cls(
                id=int(raw["id"]),
                key=str(raw["key"]),
                value=str(raw["value"]),
            )
        raise TypeError(f"Unsupported card payload type: {type(raw)!r}")


@dataclass(frozen=True)
class UserPayload:
    chat_id: int
    name: str

    @classmethod
    def from_any(cls, raw: Any) -> "UserPayload":
        if isinstance(raw, cls):
            return raw
        if isinstance(raw, Mapping):
            return cls(chat_id=int(raw["chat_id"]), name=str(raw["name"]))
        raise TypeError(f"Unsupported user payload type: {type(raw)!r}")


@dataclass
class PlayerState:
    user_id: int
    name: str
    role: str = "player"
    is_captain: bool = False

    @classmethod
    def from_any(cls, raw: Any) -> "PlayerState":
        if isinstance(raw, cls):
            return raw
        if isinstance(raw, Mapping):
            return cls(
                user_id=int(raw["user_id"]),
                name=str(raw.get("name", "")),
                role=str(raw.get("role", "player")),
                is_captain=bool(raw.get("is_captain", False)),
            )
        raise TypeError(f"Unsupported player payload type: {type(raw)!r}")


@dataclass
class RoundInfoEntry:
    round_id: int
    key: str
    value: str | int

    @classmethod
    def from_any(cls, raw: Any) -> "RoundInfoEntry":
        if isinstance(raw, cls):
            return raw
        if isinstance(raw, Mapping):
            return cls(
                round_id=int(raw["round_id"]),
                key=str(raw["key"]),
                value=raw["value"],
            )
        raise TypeError(f"Unsupported round info payload type: {type(raw)!r}")
