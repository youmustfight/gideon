"""document_content_image

Revision ID: df8be2164356
Revises: a177d4bb0629
Create Date: 2022-11-09 08:23:55.626723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df8be2164356'
down_revision = 'a177d4bb0629'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documentcontent", sa.Column('image_file_id', sa.Integer, sa.ForeignKey('file.id')))


def downgrade() -> None:
    op.drop_column("documentcontent", "image_file_id")
