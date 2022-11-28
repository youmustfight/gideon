"""created-ats

Revision ID: 42335cd966ae
Revises: a95631dc9533
Create Date: 2022-11-27 22:10:00.988725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42335cd966ae'
down_revision = 'a95631dc9533'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("case", sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("document", sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("documentcontent", sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("embedding", sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("file", sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("organization", sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("user", sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column("case", "created_at")
    op.drop_column("document", "created_at")
    op.drop_column("documentcontent", "created_at")
    op.drop_column("embedding", "created_at")
    op.drop_column("file", "created_at")
    op.drop_column("organization", "created_at")
    op.drop_column("user", "created_at")
