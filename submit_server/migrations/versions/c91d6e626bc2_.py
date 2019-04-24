"""empty message

Revision ID: c91d6e626bc2
Revises: f9b1d64b021e
Create Date: 2019-04-23 19:01:42.099647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c91d6e626bc2'
down_revision = 'f9b1d64b021e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('repo_stat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inchi', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('training_run', sa.Column('_rxn_temperatureC_actual_bulk', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('training_run', '_rxn_temperatureC_actual_bulk')
    op.drop_table('repo_stat')
    # ### end Alembic commands ###