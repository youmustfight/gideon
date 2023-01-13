"""fix-cap-case-content-relation-to-cap-case

Revision ID: 59ae3dbbeacd
Revises: 7591800223d7
Create Date: 2023-01-12 19:20:55.890240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59ae3dbbeacd'
down_revision = '7591800223d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('cap_case_content', 'cap_case_id')
    op.add_column("cap_case_content", sa.Column('cap_case_id', sa.Integer, sa.ForeignKey('cap_case.id')))


def downgrade() -> None:
    op.drop_column('cap_case_content', 'cap_case_id')
    op.add_column("cap_case_content", sa.Column('cap_case_id', sa.Integer, sa.ForeignKey('case.id')))
