"""rename-seconds-columns

Revision ID: 03fff646d301
Revises: d930498af1df
Create Date: 2022-12-11 13:23:21.819538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03fff646d301'
down_revision = 'd930498af1df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("documentcontent", "start_second", new_column_name="second_start")
    op.alter_column("documentcontent", "end_second", new_column_name="second_end")
    op.alter_column("documentcontent", "patch_size", new_column_name="image_patch_size")


def downgrade() -> None:
    op.alter_column("documentcontent", "second_start", new_column_name="start_second")
    op.alter_column("documentcontent", "second_end", new_column_name="end_second")
    op.alter_column("documentcontent", "image_patch_size", new_column_name="patch_size")
