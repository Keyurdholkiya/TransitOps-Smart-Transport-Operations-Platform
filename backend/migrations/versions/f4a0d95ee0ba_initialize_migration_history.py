"""initialize migration history

Revision ID: f4a0d95ee0ba
Revises:
Create Date: 2026-07-12 10:16:48.214680

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "f4a0d95ee0ba"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
