"""embedding-action-index-partition

Revision ID: 0c3bf264eb3b
Revises: 0fc03f984827
Create Date: 2022-12-19 18:30:05.596274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c3bf264eb3b'
down_revision = '0fc03f984827'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('embedding', 'content_type')
    op.add_column('embedding', sa.Column('ai_action', sa.Text()))
    op.add_column('embedding', sa.Column('index_id', sa.Text()))
    op.add_column('embedding', sa.Column('index_partition_id', sa.Text()))
    op.add_column('embedding', sa.Column('indexed_status', sa.Text()))

def downgrade() -> None:
    op.add_column('embedding', sa.Column('content_type', sa.Text()))
    op.drop_column('embedding', 'ai_action')
    op.drop_column('embedding', 'index_id')
    op.drop_column('embedding', 'index_partition_id')
    op.drop_column('embedding', 'indexed_status')
