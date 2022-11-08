"""embedding_vectors

Revision ID: 1d07918b98c7
Revises: 83f8745762a4
Create Date: 2022-11-08 16:01:47.794078

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '1d07918b98c7'
down_revision = '83f8745762a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('embedding', sa.Column('vector_json', JSONB))
    op.drop_column('embedding', 'text')

def downgrade() -> None:
    op.drop_column('embedding', 'vector')
    sa.Column('text', sa.Text()),
