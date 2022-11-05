"""embeddings

Revision ID: fa408b29ac7b
Revises: e7412e633083
Create Date: 2022-11-05 17:53:12.142106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa408b29ac7b'
down_revision = 'e7412e633083'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'embedding',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('document_id', sa.Integer, sa.ForeignKey('document.id')),
        sa.Column('document_content_id', sa.Integer, sa.ForeignKey('documentcontent.id')),
        sa.Column('encoded_model', sa.Text()),
        sa.Column('encoded_model_engine', sa.Text()),
        sa.Column('encoding_strategy', sa.Text()),
        sa.Column('text', sa.Text()),
        sa.Column('npy_url', sa.Text()),
    )


def downgrade() -> None:
    op.drop_table('embedding')
