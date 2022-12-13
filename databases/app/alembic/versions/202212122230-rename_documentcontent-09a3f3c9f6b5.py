"""rename-documentcontent

Revision ID: 09a3f3c9f6b5
Revises: b9492f470b28
Create Date: 2022-12-12 22:30:00.889195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09a3f3c9f6b5'
down_revision = 'b9492f470b28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('documentcontent', 'document_content')


def downgrade() -> None:
    op.rename_table('document_content', 'documentcontent')
