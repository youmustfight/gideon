"""writing-template

Revision ID: b3e6d7dff989
Revises: eb92682711f5
Create Date: 2022-12-13 22:21:52.716406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3e6d7dff989'
down_revision = 'eb92682711f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('writing', sa.Column('is_template', sa.Boolean()))
    op.add_column('writing', sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organization.id')))
    op.add_column('writing', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column('writing', 'is_template')
    op.drop_column('writing', 'organization_id')
    op.drop_column('writing', 'created_at')
