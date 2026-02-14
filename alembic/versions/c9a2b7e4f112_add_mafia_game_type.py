"""Add mafia game_type

Revision ID: c9a2b7e4f112
Revises: f4a7c2d19b11
Create Date: 2026-02-14 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9a2b7e4f112"
down_revision: Union[str, None] = "f4a7c2d19b11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    existing_id = conn.execute(
        sa.text("SELECT id FROM game_type WHERE name = :name"),
        {"name": "mafia"},
    ).scalar()
    if existing_id is None:
        conn.execute(sa.text("INSERT INTO game_type (name) VALUES (:name)"), {"name": "mafia"})


def downgrade() -> None:
    conn = op.get_bind()
    mafia_id = conn.execute(
        sa.text("SELECT id FROM game_type WHERE name = :name"),
        {"name": "mafia"},
    ).scalar()
    if mafia_id is None:
        return

    conn.execute(
        sa.text("DELETE FROM game_type_card WHERE game_type_id = :game_type_id"),
        {"game_type_id": int(mafia_id)},
    )
    conn.execute(sa.text("DELETE FROM game_type WHERE id = :id"), {"id": int(mafia_id)})
