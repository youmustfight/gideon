"""user-action-locks

Revision ID: 94cffa44968d
Revises: e6e5d9807aa5
Create Date: 2023-01-10 22:30:26.534179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94cffa44968d'
down_revision = 'e6e5d9807aa5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_action_lock", sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')))


def downgrade() -> None:
    op.drop_column('ai_action_lock', 'user_id')
