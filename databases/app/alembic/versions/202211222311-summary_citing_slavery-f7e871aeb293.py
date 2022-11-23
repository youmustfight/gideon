"""summary-citing-slavery

Revision ID: f7e871aeb293
Revises: 6c44117e91e6
Create Date: 2022-11-22 23:11:32.541278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7e871aeb293'
down_revision = '6c44117e91e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('document', sa.Column('document_citing_slavery_summary', sa.Text))


def downgrade() -> None:
    op.drop_column('document', 'document_citing_slavery_summary')
