"""embedding-cap-case-relation

Revision ID: b68c8c799b6d
Revises: 6bca7939f172
Create Date: 2023-01-12 15:59:43.043449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b68c8c799b6d'
down_revision = '6bca7939f172'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("embedding", sa.Column('cap_case_id', sa.Integer, sa.ForeignKey('cap_case.id')))


def downgrade() -> None:
    op.drop_column('embedding', 'cap_case_id')
