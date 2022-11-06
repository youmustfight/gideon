"""document_relationships

Revision ID: e7412e633083
Revises: 68b560f77a37
Create Date: 2022-11-05 17:35:27.184816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7412e633083'
down_revision = '68b560f77a37'
branch_labels = None
depends_on = None


def upgrade() -> None:
     op.add_column('documentcontent', sa.Column('document_id', sa.Integer, sa.ForeignKey('document.id')))
     op.add_column('file', sa.Column('document_id', sa.Integer, sa.ForeignKey('document.id')))


def downgrade() -> None:
    op.drop_column('documentcontent', 'document_id')
    op.drop_column('file', 'document_id')
