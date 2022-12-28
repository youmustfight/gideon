"""document-summary-rename

Revision ID: 60a491356ec2
Revises: a625ba934fc6
Create Date: 2022-12-28 16:18:32.405992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60a491356ec2'
down_revision = 'a625ba934fc6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('document', 'document_description', new_column_name='generated_description')
    op.alter_column('document', 'document_events', new_column_name='generated_events')
    op.alter_column('document', 'document_summary', new_column_name='generated_summary')
    op.alter_column('document', 'document_summary_one_liner', new_column_name='generated_summary_one_liner')


def downgrade() -> None:
    op.alter_column('document', 'generated_description', new_column_name='document_description')
    op.alter_column('document', 'generated_events', new_column_name='document_events')
    op.alter_column('document', 'generated_summary', new_column_name='document_summary')
    op.alter_column('document', 'generated_summary_one_liner', new_column_name='document_summary_one_liner')
