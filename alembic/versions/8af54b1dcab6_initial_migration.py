"""initial migration

Revision ID: 8af54b1dcab6
Revises: c1c93a51504f
Create Date: 2024-10-11 16:17:11.511637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8af54b1dcab6'
down_revision: Union[str, None] = 'c1c93a51504f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
