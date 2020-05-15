"""empty message

Revision ID: c34a3d8f38fb
Revises: 50425320898b
Create Date: 2020-05-13 02:37:00.719422

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c34a3d8f38fb"
down_revision = "50425320898b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BIGINT(), nullable=True),
        sa.Column("guild_id", sa.BIGINT(), nullable=True),
        sa.Column("birthday", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "guild_id", name="guild_user"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    # ### end Alembic commands ###
