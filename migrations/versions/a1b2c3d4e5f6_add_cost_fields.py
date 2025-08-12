"""add cost snapshot fields to time_entry
Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2025-08-12 17:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('time_entry', sa.Column('hourly_rate_applied', sa.Float(), nullable=True))
    op.add_column('time_entry', sa.Column('burden_percent_applied', sa.Float(), nullable=True))
    op.add_column('time_entry', sa.Column('labor_cost', sa.Float(), nullable=True))
    op.add_column('time_entry', sa.Column('total_cost', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('time_entry', 'total_cost')
    op.drop_column('time_entry', 'labor_cost')
    op.drop_column('time_entry', 'burden_percent_applied')
    op.drop_column('time_entry', 'hourly_rate_applied')
