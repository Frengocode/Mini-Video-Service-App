"""Create View table

Revision ID: 332e498d0362
Revises: 
Create Date: 2024-10-10 14:01:02.885087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision: str = '332e498d0362'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.create_table('views',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('video_id', sa.Integer(), nullable=True),
    sa.Column('viewed_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_views_id'), 'views', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_views_id'), table_name='views')
    op.drop_table('views')
    # ### end Alembic commands ###