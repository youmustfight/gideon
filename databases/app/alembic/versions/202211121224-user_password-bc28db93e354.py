"""user_password

Revision ID: bc28db93e354
Revises: 9f6d67f706e2
Create Date: 2022-11-12 12:24:59.105990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc28db93e354'
down_revision = '9f6d67f706e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('user', sa.Column('password', sa.Text))


def downgrade() -> None:
    op.drop_column('user', 'password')
