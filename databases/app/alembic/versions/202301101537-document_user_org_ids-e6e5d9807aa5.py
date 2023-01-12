"""document-user-org-ids

Revision ID: e6e5d9807aa5
Revises: dcc09b64cd8d
Create Date: 2023-01-10 15:37:33.796374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6e5d9807aa5'
down_revision = 'dcc09b64cd8d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column('organization_id', sa.Integer, sa.ForeignKey('organization.id')))
    op.add_column("document", sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id')))


def downgrade() -> None:
    op.drop_column('document', 'organization_id')
    op.drop_column('document', 'user_id')
