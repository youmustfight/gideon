"""cap-case-v2

Revision ID: d151402dbe40
Revises: 7037deca95c4
Create Date: 2022-12-25 12:48:28.536379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd151402dbe40'
down_revision = '7037deca95c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('cap_caselaw', 'document_summary', new_column_name='generated_summary')
    op.alter_column('cap_caselaw', 'document_summary_one_liner', new_column_name='generated_summary_one_liner')
    op.alter_column('cap_caselaw', 'document_citing_slavery_summary', new_column_name='generated_citing_slavery_summary')
    op.alter_column('cap_caselaw', 'document_citing_slavery_summary_one_liner', new_column_name='generated_citing_slavery_summary_one_liner')
    op.rename_table('cap_caselaw', 'cap_case')
    # summaries regarding citing slavery etc. should be on case level, not doc level
    op.drop_column('document', 'document_citing_slavery_summary')
    op.drop_column('document', 'document_citing_slavery_summary_one_liner')


def downgrade() -> None:
    op.alter_column('cap_case', 'generated_summary', new_column_name='document_summary')
    op.alter_column('cap_case', 'generated_summary_one_liner', new_column_name='document_summary_one_liner')
    op.alter_column('cap_case', 'generated_citing_slavery_summary', new_column_name='document_citing_slavery_summary')
    op.alter_column('cap_case', 'generated_citing_slavery_summary_one_liner', new_column_name='document_citing_slavery_summary_one_liner')
    op.rename_table('cap_case', 'cap_caselaw')
    # add back legacy column
    op.add_column('document', sa.Column('document_citing_slavery_summary', sa.Text))
    op.add_column('document', sa.Column('document_citing_slavery_summary_one_liner', sa.Text))
