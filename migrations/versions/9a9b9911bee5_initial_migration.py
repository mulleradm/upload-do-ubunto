"""Initial migration

Revision ID: 9a9b9911bee5
Revises: 
Create Date: 2025-01-02 04:32:31.649008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a9b9911bee5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attempt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('attempt', sa.String(length=20), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('safe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('combination', sa.String(length=20), nullable=False),
    sa.Column('prize', sa.String(length=255), nullable=False),
    sa.Column('donor', sa.String(length=100), nullable=False),
    sa.Column('reset_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('safe')
    op.drop_table('attempt')
    # ### end Alembic commands ###