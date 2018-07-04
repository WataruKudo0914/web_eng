"""empty message

Revision ID: c8b886dea75d
Revises: 89a61fa29a93
Create Date: 2018-07-01 20:28:59.545473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8b886dea75d'
down_revision = '89a61fa29a93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('goods_table', sa.Column('goods_id', sa.Integer(), nullable=False))
    op.drop_column('goods_table', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('goods_table', sa.Column('id', sa.INTEGER(), nullable=False))
    op.drop_column('goods_table', 'goods_id')
    # ### end Alembic commands ###
