"""case_init

Revision ID: 521ee1f6a6b7
Revises: 3e508b00dbfa
Create Date: 2022-11-05 16:53:05.780594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '521ee1f6a6b7'
down_revision = '3e508b00dbfa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'case',
        sa.Column('id', sa.Integer, primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('case')
