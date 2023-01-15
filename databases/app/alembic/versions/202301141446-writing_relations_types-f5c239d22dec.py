"""writing-relations-types

Revision ID: f5c239d22dec
Revises: 59ae3dbbeacd
Create Date: 2023-01-14 14:46:40.024904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5c239d22dec'
down_revision = '59ae3dbbeacd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('writing', sa.Column('type', sa.Text()))
    op.add_column("writing", sa.Column('document_id', sa.Integer, sa.ForeignKey('document.id')))
    op.add_column("writing", sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')))


def downgrade() -> None:
    op.drop_column('writing', 'type')
    op.drop_column('writing', 'document_id')
    op.drop_column('writing', 'user_id')
