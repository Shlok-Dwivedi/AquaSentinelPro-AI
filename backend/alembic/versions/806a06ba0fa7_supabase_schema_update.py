"""supabase schema update

Revision ID: 806a06ba0fa7
Revises: 971f7a30b99f
Create Date: 2026-07-19 23:21:00.552932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '806a06ba0fa7'
down_revision: Union[str, Sequence[str], None] = '971f7a30b99f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('name',
                   existing_type=sa.VARCHAR(length=100),
                   nullable=False)
        batch_op.drop_column('email')
        batch_op.drop_column('created_at')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('email', sa.VARCHAR(length=255), nullable=True))
        batch_op.alter_column('name',
                   existing_type=sa.VARCHAR(length=100),
                   nullable=True)
