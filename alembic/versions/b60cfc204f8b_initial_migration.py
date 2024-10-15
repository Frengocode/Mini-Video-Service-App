"""initial migration

Revision ID: b60cfc204f8b
Revises: 8af54b1dcab6
Create Date: 2024-10-11 21:34:31.829677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b60cfc204f8b'
down_revision: Union[str, None] = '8af54b1dcab6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
