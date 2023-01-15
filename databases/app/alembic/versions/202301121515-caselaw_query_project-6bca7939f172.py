"""caselaw_query_project

Revision ID: 6bca7939f172
Revises: 94cffa44968d
Create Date: 2023-01-12 15:15:42.017742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bca7939f172'
down_revision = '94cffa44968d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cap_case', sa.Column('project_tag', sa.Text()))


def downgrade() -> None:
    op.drop_column('cap_case', 'project_tag')
