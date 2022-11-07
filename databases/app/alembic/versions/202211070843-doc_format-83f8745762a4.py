"""doc-format

Revision ID: 83f8745762a4
Revises: fa408b29ac7b
Create Date: 2022-11-07 08:43:09.722743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83f8745762a4'
down_revision = 'fa408b29ac7b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('document', sa.Column('name', sa.Text))
    op.add_column('document', sa.Column('type', sa.String))


def downgrade() -> None:
    op.drop_column('document', 'name')
    op.drop_column('document', 'type')
