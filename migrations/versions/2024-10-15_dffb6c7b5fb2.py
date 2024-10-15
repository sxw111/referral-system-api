"""Initial tables

Revision ID: dffb6c7b5fb2
Revises:
Create Date: 2024-10-15 13:50:15.629425

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dffb6c7b5fb2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("referral_code", sa.String(length=8), nullable=True),
        sa.Column("referral_code_exp", sa.DateTime(), nullable=True),
        sa.Column("referer_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["referer_id"], ["users.id"], name=op.f("fk_users_referer_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("referral_code", name=op.f("uq_users_referral_code")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    # ### end Alembic commands ###
