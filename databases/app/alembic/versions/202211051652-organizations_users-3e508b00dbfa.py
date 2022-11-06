"""organizations_users

Revision ID: 3e508b00dbfa
Revises: 
Create Date: 2022-11-05 16:52:37.492815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e508b00dbfa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=True),
    )
    op.create_table(
        'organization',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('user')
    op.drop_table('organization')
