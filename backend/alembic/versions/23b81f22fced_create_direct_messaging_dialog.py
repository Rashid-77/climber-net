"""create direct messaging "dialog"

Revision ID: 172994740916
Revises: 23b81f22fced
Create Date: 2023-11-27 17:07:11.757869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# revision: str = '172994740916'
# down_revision: Union[str, None] = '23b81f22fced'
revision: str = '23b81f22fced'
down_revision: Union[str, None] = '459f179f47a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("dialog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("from_user_id", sa.Integer(), nullable=False),
        sa.Column("to_user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column("read", sa.Boolean(), default=False),
        sa.Column("del_by_sender", sa.Boolean(), default=False),
        sa.Column("del_by_recipient", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["from_user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )


def downgrade() -> None:
    op.drop_table("dialog")
