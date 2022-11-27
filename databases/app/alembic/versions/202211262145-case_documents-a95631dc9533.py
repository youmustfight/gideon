"""case-documents

Revision ID: a95631dc9533
Revises: d2000807c966
Create Date: 2022-11-26 21:45:02.179513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a95631dc9533'
down_revision = 'd2000807c966'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')))


def downgrade() -> None:
    op.drop_column("document", "case_id")
