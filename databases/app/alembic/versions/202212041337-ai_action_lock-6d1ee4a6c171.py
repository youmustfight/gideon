"""ai-action-lock

Revision ID: 6d1ee4a6c171
Revises: e43e8a8dd325
Create Date: 2022-12-04 13:37:37.171469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d1ee4a6c171'
down_revision = 'e43e8a8dd325'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ai_action_lock',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('action', sa.Text),
        sa.Column('model_name', sa.Text),
        sa.Column('params', sa.JSON),
        # relations
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        # meta
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('ai_action_lock')
