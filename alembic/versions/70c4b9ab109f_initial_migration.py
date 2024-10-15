"""initial migration

Revision ID: 70c4b9ab109f
Revises: b60cfc204f8b
Create Date: 2024-10-11 21:35:19.920294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70c4b9ab109f'
down_revision: Union[str, None] = 'b60cfc204f8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('date_pub', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('comment', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_table('comments')