"""case-fact-updated-created-at

Revision ID: 784d61431a52
Revises: 8918d72f14d9
Create Date: 2022-12-18 20:41:46.494728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '784d61431a52'
down_revision = '8918d72f14d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('case_fact', sa.Column('updated_at', sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column('case_fact', sa.Column('updated_at'))
