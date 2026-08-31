"""add matched_rules to alerts

Revision ID: a1b2c3d4e5f6
Revises: ee467f8c6f3c
Create Date: 2026-08-31 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'ee467f8c6f3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('alerts', sa.Column('matched_rules', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('alerts', 'matched_rules')
