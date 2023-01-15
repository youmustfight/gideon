"""embedding-cap-case-content

Revision ID: 7591800223d7
Revises: 5c0631f2511c
Create Date: 2023-01-12 18:28:01.644090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7591800223d7'
down_revision = '5c0631f2511c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("embedding", sa.Column('cap_case_content_id', sa.Integer, sa.ForeignKey('cap_case_content.id')))


def downgrade() -> None:
    op.drop_column('embedding', 'cap_case_content_id')
