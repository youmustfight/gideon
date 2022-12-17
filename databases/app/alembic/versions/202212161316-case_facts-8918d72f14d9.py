"""case-facts

Revision ID: 8918d72f14d9
Revises: b3e6d7dff989
Create Date: 2022-12-16 13:16:25.233307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8918d72f14d9'
down_revision = 'b3e6d7dff989'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'case_fact',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        sa.Column('text', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.add_column('writing', sa.Column('generated_body_html', sa.Text()))
    op.add_column('writing', sa.Column('generated_body_text', sa.Text()))
    op.add_column('writing', sa.Column('forked_writing_id', sa.Integer, sa.ForeignKey('writing.id')),)


def downgrade() -> None:
    op.drop_table('case_fact')
    op.drop_column('writing', 'generated_body_html')
    op.drop_column('writing', 'generated_body_text')
    op.drop_column('writing', 'forked_writing_id')
