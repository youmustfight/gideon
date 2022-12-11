"""sentence-start-end

Revision ID: d930498af1df
Revises: 6d1ee4a6c171
Create Date: 2022-12-11 10:55:26.784643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd930498af1df'
down_revision = '6d1ee4a6c171'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documentcontent", sa.Column('sentence_number', sa.Integer))
    op.add_column("documentcontent", sa.Column('sentence_start', sa.Integer))
    op.add_column("documentcontent", sa.Column('sentence_end', sa.Integer))


def downgrade() -> None:
    op.drop_column("documentcontent", "sentence_number")
    op.drop_column("documentcontent", "sentence_start")
    op.drop_column("documentcontent", "sentence_end")
