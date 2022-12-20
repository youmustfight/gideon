"""action-locks-index-info

Revision ID: c86cc48c8d55
Revises: 0c3bf264eb3b
Create Date: 2022-12-19 19:23:31.410959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c86cc48c8d55'
down_revision = '0c3bf264eb3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ai_action_lock', sa.Column('index_id', sa.Text()))
    op.add_column('ai_action_lock', sa.Column('index_partition_id', sa.Text()))



def downgrade() -> None:
    op.drop_column('ai_action_lock', 'index_id')
    op.drop_column('ai_action_lock', 'index_partition_id')
