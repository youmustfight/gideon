"""cap-caselaw-init

Revision ID: 2e9d47148748
Revises: 03fff646d301
Create Date: 2022-12-12 11:00:18.103321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e9d47148748'
down_revision = '03fff646d301'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cap_caselaw',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('cap_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text()),
        sa.Column('name', sa.Text()),
        sa.Column('name_abbreviation', sa.Text()),
        sa.Column('decision_date', sa.Text()),
        sa.Column('docket_number', sa.Text()),
        sa.Column('first_page', sa.Text()),
        sa.Column('last_page', sa.Text()),
        sa.Column('citations', sa.JSON()),
        sa.Column('volume', sa.JSON()),
        sa.Column('reporter', sa.JSON()),
        sa.Column('court', sa.JSON()),
        sa.Column('jurisdiction', sa.JSON()),
        sa.Column('cites_to', sa.JSON()),
        sa.Column('frontend_url', sa.Text()),
        sa.Column('frontend_pdf_url', sa.Text()),
        sa.Column('preview', sa.JSON()),
        sa.Column('analysis', sa.JSON()),
        sa.Column('last_updated', sa.Text()),
        sa.Column('provenance', sa.JSON()),
        sa.Column('casebody', sa.JSON()),
    )


def downgrade() -> None:
    op.drop_table('cap_caselaw')
