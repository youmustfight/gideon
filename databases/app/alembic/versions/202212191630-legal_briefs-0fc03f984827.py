"""legal-briefs

Revision ID: 0fc03f984827
Revises: 151f93aab2f9
Create Date: 2022-12-19 16:30:52.172621

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '0fc03f984827'
down_revision = '151f93aab2f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('case_fact', 'legal_brief_fact')
    op.add_column("embedding", sa.Column('case_id', sa.Integer, sa.ForeignKey('case.id')))


def downgrade() -> None:
    op.rename_table('legal_brief_fact', 'case_fact')
    op.drop_column('embedding', 'case_id')