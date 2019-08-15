"""empty message

Revision ID: 8bf77f688e95
Revises: 4658f6697b50
Create Date: 2019-08-15 15:17:01.419595

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8bf77f688e95'
down_revision = '4658f6697b50'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('repo_stat', 'reproducibility_stat')


def downgrade():
    op.rename_table('reproducibility_stat', 'repo_stat')

