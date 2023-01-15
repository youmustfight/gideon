"""cap-case-timestamps

Revision ID: 5c0631f2511c
Revises: eaf5c417d73d
Create Date: 2023-01-12 18:23:47.990095

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c0631f2511c'
down_revision = 'eaf5c417d73d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cap_case', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('cap_case', sa.Column('updated_at', sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column('cap_case', 'created_at')
    op.drop_column('cap_case', 'updated_at')
