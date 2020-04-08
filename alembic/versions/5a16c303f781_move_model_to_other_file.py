"""Move model to other file

Revision ID: 5a16c303f781
Revises: 6846673cde7e
Create Date: 2020-04-08 22:35:41.721496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a16c303f781'
down_revision = '6846673cde7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guilds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prefix', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('guilds')
    # ### end Alembic commands ###