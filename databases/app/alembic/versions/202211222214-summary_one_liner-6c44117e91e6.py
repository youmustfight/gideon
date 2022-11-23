"""summary-one-liner

Revision ID: 6c44117e91e6
Revises: ffacec964855
Create Date: 2022-11-22 22:14:18.789293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c44117e91e6'
down_revision = 'ffacec964855'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('document', sa.Column('document_summary_one_liner', sa.Text))


def downgrade() -> None:
    op.drop_column('document', 'document_summary_one_liner')
