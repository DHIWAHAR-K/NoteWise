"""initial db_health

Revision ID: 20250405_0001
Revises:
Create Date: 2025-04-05

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250405_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "db_health",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ok", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(sa.text("INSERT INTO db_health (ok) VALUES (true)"))


def downgrade() -> None:
    op.drop_table("db_health")
