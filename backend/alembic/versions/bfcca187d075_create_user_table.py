"""Create user table

Revision ID: bfcca187d075
Revises: 
Create Date: 2024-04-10 13:00:35.240908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'bfcca187d075'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, unique=True, index=True, nullable=False),
        sa.Column('first_name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('strava_id', sa.String, unique=True, nullable=True),
        sa.Column('strava_access_token', sa.String, nullable=True),
        sa.Column('strava_refresh_token', sa.String, nullable=True),
        sa.Column('strava_expires_at', sa.Integer, nullable=True)
    )
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
