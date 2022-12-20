"""embedding-content-types

Revision ID: 151f93aab2f9
Revises: 784d61431a52
Create Date: 2022-12-19 15:58:07.186493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '151f93aab2f9'
down_revision = '784d61431a52'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('embedding', sa.Column('content_type', sa.Text()))


def downgrade() -> None:
    op.drop_column('embedding', 'content_type')
