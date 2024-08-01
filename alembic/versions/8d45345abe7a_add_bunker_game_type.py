"""Add bunker game_type

Revision ID: 8d45345abe7a
Revises: ab4aa22fc5d0
Create Date: 2024-08-01 14:19:06.234215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer


# revision identifiers, used by Alembic.
revision: str = '8d45345abe7a'
down_revision: Union[str, None] = 'ab4aa22fc5d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

game_type_table = table('game_type',
    column('id', Integer),
    column('name', String)
)
def upgrade() -> None:
    op.bulk_insert(game_type_table,
        [
            {'id': 2, 'name': 'bunker'}
        ]
    )

def downgrade() -> None:
    op.execute('DELETE FROM game_type WHERE id IN (2)')
