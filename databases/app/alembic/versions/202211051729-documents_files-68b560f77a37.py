"""documents_files

Revision ID: 68b560f77a37
Revises: 24797178574c
Create Date: 2022-11-05 17:29:17.283405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68b560f77a37'
down_revision = '24797178574c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'document',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('status_processing_files', sa.String(), nullable=True),
        sa.Column('status_processing_embeddings', sa.String(), nullable=True),
        sa.Column('document_description', sa.Text(), nullable=True),
        sa.Column('document_summary', sa.Text(), nullable=True),
    )
    op.create_table(
        'documentcontent',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('tokenizing_strategy', sa.String(), nullable=True),
        sa.Column('page_number', sa.String(), nullable=True),
    )
    op.create_table(
        'file',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('filename', sa.Text(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('upload_key', sa.String(), nullable=True),
        sa.Column('upload_url', sa.String(), nullable=True),
        sa.Column('upload_thumbnail_url', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('document')
    op.drop_table('documentcontent')
    op.drop_table('file')
