"""empty message

Revision ID: 1623f7ae0dfb
Revises: e877446e82ec
Create Date: 2020-05-13 02:27:10.952134

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1623f7ae0dfb'
down_revision = 'e877446e82ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_id', sa.BIGINT(), nullable=True))
    op.alter_column('users', 'guild_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.create_unique_constraint('guild_user', 'users', ['user_id', 'guild_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('guild_user', 'users', type_='unique')
    op.alter_column('users', 'guild_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.drop_column('users', 'user_id')
    # ### end Alembic commands ###
