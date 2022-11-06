"""case_orgs_users_relationships

Revision ID: 24797178574c
Revises: 521ee1f6a6b7
Create Date: 2022-11-05 16:58:55.338670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24797178574c'
down_revision = '521ee1f6a6b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'organization_case',
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        sa.Column('organization_id', sa.Integer, sa.ForeignKey('organization.id')),
    )
    op.create_table(
        'organization_user',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('organization_id', sa.Integer, sa.ForeignKey('organization.id')),
    )
    op.create_table(
        'case_user',
        sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')),
    )


def downgrade() -> None:
    op.drop_table('organization_case')
    op.drop_table('organization_user')
    op.drop_table('case_user')
