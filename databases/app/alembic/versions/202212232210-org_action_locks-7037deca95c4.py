"""org-action-locks

Revision ID: 7037deca95c4
Revises: 35300b6f8bb1
Create Date: 2022-12-23 22:10:16.461301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7037deca95c4'
down_revision = '35300b6f8bb1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_action_lock", sa.Column('organization_id', sa.Integer, sa.ForeignKey('organization.id')))


def downgrade() -> None:
    op.drop_column('ai_action_lock', 'organization_id')
