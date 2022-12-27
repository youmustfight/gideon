"""cap-case-statuses

Revision ID: a625ba934fc6
Revises: d151402dbe40
Create Date: 2022-12-26 12:50:04.637061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a625ba934fc6'
down_revision = 'd151402dbe40'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cap_case', sa.Column('status_processing_content', sa.Text))
    op.add_column('cap_case', sa.Column('status_processing_embeddings', sa.Text))
    op.add_column('cap_case', sa.Column('status_processing_extractions', sa.Text))


def downgrade() -> None:
    op.drop_column('cap_case', 'status_processing_content')
    op.drop_column('cap_case', 'status_processing_embeddings')
    op.drop_column('cap_case', 'status_processing_extractions')
