"""empty message

Revision ID: 1076d5169c91
Revises: d19d0bd20b7b
Create Date: 2019-04-23 21:33:48.192070

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1076d5169c91'
down_revision = 'd19d0bd20b7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('repo_stat', sa.Column('acid', sa.Float(), nullable=True))
    op.add_column('repo_stat', sa.Column('inorganic', sa.Float(), nullable=True))
    op.add_column('repo_stat', sa.Column('organic', sa.Float(), nullable=True))
    op.add_column('repo_stat', sa.Column('repo', sa.Float(), nullable=True))
    op.add_column('repo_stat', sa.Column('score', sa.Float(), nullable=True))
    op.add_column('repo_stat', sa.Column('size', sa.Integer(), nullable=True))
    op.add_column('repo_stat', sa.Column('temp', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('repo_stat', 'temp')
    op.drop_column('repo_stat', 'size')
    op.drop_column('repo_stat', 'score')
    op.drop_column('repo_stat', 'repo')
    op.drop_column('repo_stat', 'organic')
    op.drop_column('repo_stat', 'inorganic')
    op.drop_column('repo_stat', 'acid')
    # ### end Alembic commands ###