"""create post table

Revision ID: 459f179f47a3
Revises: 0729aaa33f78
Create Date: 2023-11-17 14:47:44.921934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

from models.post import PostPrivacy

# revision identifiers, used by Alembic.
revision: str = '459f179f47a3'
down_revision: Union[str, None] = '0729aaa33f78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("post",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("wall_user_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("privacy", sa.Integer(), default=PostPrivacy.PUBLIC, nullable=False),
        sa.Column("comments_count", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wall_user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )

def downgrade() -> None:
    op.drop_table("post")