"""briefs-v1

Revision ID: 24fa793c3ab9
Revises: 60a491356ec2
Create Date: 2022-12-28 17:22:23.494446

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '24fa793c3ab9'
down_revision = '60a491356ec2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'brief',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        sa.Column('cap_case_id', sa.Integer, sa.ForeignKey('cap_case.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('facts', JSONB()),
        sa.Column('issues', JSONB()),
    )


def downgrade() -> None:
    op.drop_table('brief')
