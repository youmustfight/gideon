"""embedding-type-dimensions

Revision ID: e43e8a8dd325
Revises: 28a5fe83fd3a
Create Date: 2022-12-03 22:05:10.248714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e43e8a8dd325'
down_revision = '28a5fe83fd3a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("embedding", sa.Column('vector_dimensions', sa.Integer))
    op.alter_column("embedding", "encoded_model", new_column_name="encoded_model_type")

def downgrade() -> None:
    op.drop_column("embedding", "vector_dimensions")
    op.alter_column("embedding", "encoded_model_type", new_column_name="encoded_model")
