"""cap-caselaw-extras

Revision ID: b9492f470b28
Revises: 2e9d47148748
Create Date: 2022-12-12 20:53:14.146286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9492f470b28'
down_revision = '2e9d47148748'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cap_caselaw', sa.Column('document_summary', sa.Text))
    op.add_column('cap_caselaw', sa.Column('document_summary_one_liner', sa.Text))
    op.add_column('cap_caselaw', sa.Column('document_citing_slavery_summary', sa.Text))
    op.add_column('cap_caselaw', sa.Column('document_citing_slavery_summary_one_liner', sa.Text))


def downgrade() -> None:
    op.drop_column('cap_caselaw', 'document_summary')
    op.drop_column('cap_caselaw', 'document_summary_one_liner')
    op.drop_column('cap_caselaw', 'document_citing_slavery_summary')
    op.drop_column('cap_caselaw', 'document_citing_slavery_summary_one_liner')
