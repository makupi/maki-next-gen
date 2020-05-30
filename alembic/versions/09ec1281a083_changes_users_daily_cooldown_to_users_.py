"""Changes users.daily_cooldown to users.last_daily, adds daily_streak

Revision ID: 09ec1281a083
Revises: 4d9184d6f3a6
Create Date: 2020-05-30 03:28:57.179896

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '09ec1281a083'
down_revision = '4d9184d6f3a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('daily_streak', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('last_daily', sa.TIMESTAMP(), nullable=True))
    op.drop_column('users', 'daily_cooldown')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('daily_cooldown', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('users', 'last_daily')
    op.drop_column('users', 'daily_streak')
    # ### end Alembic commands ###
