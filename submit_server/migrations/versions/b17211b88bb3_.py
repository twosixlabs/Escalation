"""empty message

Revision ID: b17211b88bb3
Revises: 8bf77f688e95
Create Date: 2019-10-01 11:09:45.930687

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b17211b88bb3'
down_revision = '8bf77f688e95'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('leader_board', sa.Column('leave_one_out_id', sa.String(64), nullable=True))
    op.add_column('leader_board', sa.Column('test_group', sa.String(64), nullable=True))

def downgrade():
    op.drop_column('leader_board', 'leave_one_out_id')
    op.drop_column('leader_board', 'test_group')
