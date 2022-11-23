"""summary-citing-slavery-one-liner

Revision ID: d2000807c966
Revises: f7e871aeb293
Create Date: 2022-11-23 10:53:11.328062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2000807c966'
down_revision = 'f7e871aeb293'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('document', sa.Column('document_citing_slavery_summary_one_liner', sa.Text))


def downgrade() -> None:
    op.drop_column('document', 'document_citing_slavery_summary_one_liner')
