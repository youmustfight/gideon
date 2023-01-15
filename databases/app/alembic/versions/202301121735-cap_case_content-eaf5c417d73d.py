"""cap-case-content

Revision ID: eaf5c417d73d
Revises: b68c8c799b6d
Create Date: 2023-01-12 17:35:40.779892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaf5c417d73d'
down_revision = 'b68c8c799b6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cap_case_content',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('type', sa.Text()),
        sa.Column('text', sa.Text()),
        sa.Column('paragraph_number', sa.Integer()),
        sa.Column('cap_case_id', sa.Integer, sa.ForeignKey('case.id')),
    )


def downgrade() -> None:
    op.drop_table('cap_case_content')
