"""document_content_start_end_times

Revision ID: cc49aee536f7
Revises: df8be2164356
Create Date: 2022-11-09 18:31:14.984961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc49aee536f7'
down_revision = 'df8be2164356'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documentcontent", sa.Column('start_second', sa.Integer))
    op.add_column("documentcontent", sa.Column('end_second', sa.Integer))


def downgrade() -> None:
    op.drop_column("documentcontent", "start_second")
    op.drop_column("documentcontent", "end_second")
