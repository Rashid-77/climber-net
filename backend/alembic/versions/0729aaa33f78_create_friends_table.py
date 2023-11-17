"""create friends table

Revision ID: 0729aaa33f78
Revises: 02b4077b8d30
Create Date: 2023-11-16 15:13:41.239971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0729aaa33f78'
down_revision: Union[str, None] = '02b4077b8d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from backend.models.friend import FriendshipStatus

def upgrade() -> None:
    op.create_table(
        "friend",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_a", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=True),
        sa.Column("user_b", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False, default=FriendshipStatus.UNPROCESSED),
        sa.Column("created", sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_friend_id"), "friend", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_friends_id"), table_name="friend")
    op.drop_table("friend")