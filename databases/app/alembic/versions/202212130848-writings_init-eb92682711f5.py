"""writings-init

Revision ID: eb92682711f5
Revises: 09a3f3c9f6b5
Create Date: 2022-12-13 08:48:20.268309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb92682711f5'
down_revision = '09a3f3c9f6b5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'writing',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        sa.Column('name', sa.Text()),
        sa.Column('body_html', sa.Text()),
        sa.Column('body_text', sa.Text()),
    )



def downgrade() -> None:
    op.drop_table('writing')
