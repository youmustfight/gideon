"""org-case-id

Revision ID: 35300b6f8bb1
Revises: d74b610c3385
Create Date: 2022-12-22 17:24:08.328276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35300b6f8bb1'
down_revision = 'd74b610c3385'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('organization_case')
    op.add_column("case", sa.Column('organization_id', sa.Integer, sa.ForeignKey('organization.id')))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.create_table(
        'organization_case',
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        sa.Column('organization_id', sa.Integer, sa.ForeignKey('organization.id')),
    )
    op.drop_column('case', 'organization_id')
    op.drop_column('user', 'updated_at')
