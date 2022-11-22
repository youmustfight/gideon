"""document_events

Revision ID: ffacec964855
Revises: accb2d594c55
Create Date: 2022-11-21 17:01:56.024405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffacec964855'
down_revision = 'accb2d594c55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column('document_events', sa.JSON))


def downgrade() -> None:
    op.drop_column("document", "document_events")
