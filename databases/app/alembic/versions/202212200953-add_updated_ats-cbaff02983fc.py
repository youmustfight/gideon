"""add-updated-ats

Revision ID: cbaff02983fc
Revises: c86cc48c8d55
Create Date: 2022-12-20 09:53:16.808688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbaff02983fc'
down_revision = 'c86cc48c8d55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('case', sa.Column('updated_at', sa.DateTime(timezone=True)))
    op.add_column('document', sa.Column('updated_at', sa.DateTime(timezone=True)))
    op.add_column('embedding', sa.Column('updated_at', sa.DateTime(timezone=True)))
    op.add_column('organization', sa.Column('updated_at', sa.DateTime(timezone=True)))
    op.add_column('writing', sa.Column('updated_at', sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column('case', 'updated_at')
    op.drop_column('document', 'updated_at')
    op.drop_column('embedding', 'updated_at')
    op.drop_column('organization', 'updated_at')
    op.drop_column('writing', 'updated_at')
