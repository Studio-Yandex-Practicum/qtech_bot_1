"""First migration

Revision ID: 9857f5edb387
Revises: 
Create Date: 2024-06-28 13:54:11.956134

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9857f5edb387'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('button',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.Column('is_moscow', sa.Boolean(), nullable=True),
                    sa.Column('text', sa.Text(), nullable=True),
                    sa.Column('picture', sqlalchemy_utils.types.url.URLType(),
                              nullable=True),
                    sa.Column('file', sqlalchemy_utils.types.url.URLType(),
                              nullable=True),
                    sa.Column('is_department', sa.Boolean(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('created_date', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('button')
    # ### end Alembic commands ###
