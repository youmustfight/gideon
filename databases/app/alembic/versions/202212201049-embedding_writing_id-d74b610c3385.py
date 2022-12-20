"""embedding-writing-id

Revision ID: d74b610c3385
Revises: cbaff02983fc
Create Date: 2022-12-20 10:49:39.375335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd74b610c3385'
down_revision = 'cbaff02983fc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("embedding", sa.Column('writing_id', sa.Integer, sa.ForeignKey('writing.id')))


def downgrade() -> None:
    op.drop_column('embedding', 'writing_id')
