"""patch_strategy

Revision ID: accb2d594c55
Revises: bc28db93e354
Create Date: 2022-11-14 19:33:34.890125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'accb2d594c55'
down_revision = 'bc28db93e354'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documentcontent", sa.Column('patch_size', sa.Integer))


def downgrade() -> None:
    op.drop_column("documentcontent", "patch_size")
