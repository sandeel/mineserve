"""empty message

Revision ID: fd1e23743fb1
Revises: None
Create Date: 2016-12-18 15:44:38.865568

"""

# revision identifiers, used by Alembic.
revision = 'fd1e23743fb1'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint('server_ibfk_1', 'server', type_='foreignkey')
    op.create_foreign_key(None, 'server', 'user', ['user_id'], ['id'])
    op.drop_column('server', 'owner_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server', sa.Column('owner_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'server', type_='foreignkey')
    op.create_foreign_key('server_ibfk_1', 'server', 'user', ['owner_id'], ['id'])
    op.drop_column('server', 'user_id')
    ### end Alembic commands ###