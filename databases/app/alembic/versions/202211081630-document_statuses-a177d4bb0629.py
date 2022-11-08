"""document_statuses

Revision ID: a177d4bb0629
Revises: 1d07918b98c7
Create Date: 2022-11-08 16:30:36.128825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a177d4bb0629'
down_revision = '1d07918b98c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column("status_processing_content", sa.String(), nullable=True))
    op.add_column("document", sa.Column("status_processing_extractions", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('document', 'status_processing_content')
    op.drop_column('document', 'status_processing_extractions')
