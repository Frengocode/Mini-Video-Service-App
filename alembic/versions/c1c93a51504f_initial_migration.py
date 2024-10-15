"""initial migration

Revision ID: c1c93a51504f
Revises: e187b16cf384
Create Date: 2024-10-11 16:15:59.097919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1c93a51504f'
down_revision: Union[str, None] = 'e187b16cf384'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
