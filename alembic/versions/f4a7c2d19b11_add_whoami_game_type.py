"""Add whoami game_type

Revision ID: f4a7c2d19b11
Revises: e1b6f2a9c301
Create Date: 2026-02-14 16:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4a7c2d19b11"
down_revision: Union[str, None] = "e1b6f2a9c301"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    existing_id = conn.execute(
        sa.text("SELECT id FROM game_type WHERE name = :name"),
        {"name": "whoami"},
    ).scalar()
    if existing_id is None:
        conn.execute(sa.text("INSERT INTO game_type (name) VALUES (:name)"), {"name": "whoami"})


def downgrade() -> None:
    conn = op.get_bind()
    whoami_id = conn.execute(
        sa.text("SELECT id FROM game_type WHERE name = :name"),
        {"name": "whoami"},
    ).scalar()
    if whoami_id is None:
        return

    # In case cards were added manually later, clean them up first.
    conn.execute(
        sa.text("DELETE FROM game_type_card WHERE game_type_id = :game_type_id"),
        {"game_type_id": int(whoami_id)},
    )
    conn.execute(sa.text("DELETE FROM game_type WHERE id = :id"), {"id": int(whoami_id)})
