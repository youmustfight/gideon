"""drop-legal-brief-fact

Revision ID: dcc09b64cd8d
Revises: 24fa793c3ab9
Create Date: 2022-12-30 01:27:02.968880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcc09b64cd8d'
down_revision = '24fa793c3ab9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('legal_brief_fact')


def downgrade() -> None:
    op.create_table(
        'legal_brief_fact',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        sa.Column('text', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
