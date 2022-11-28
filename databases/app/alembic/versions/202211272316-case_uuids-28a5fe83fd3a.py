"""case-uuids

Revision ID: 28a5fe83fd3a
Revises: 42335cd966ae
Create Date: 2022-11-27 23:16:23.697665

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '28a5fe83fd3a'
down_revision = '42335cd966ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("case", sa.Column('uuid', UUID()))


def downgrade() -> None:
    op.drop_column("case", "uuid")
