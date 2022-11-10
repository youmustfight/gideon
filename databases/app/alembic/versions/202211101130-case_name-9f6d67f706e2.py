"""case_name

Revision ID: 9f6d67f706e2
Revises: cc49aee536f7
Create Date: 2022-11-10 11:30:38.784502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f6d67f706e2'
down_revision = 'cc49aee536f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('case', sa.Column('name', sa.Text))


def downgrade() -> None:
    op.drop_column('case', 'name')
