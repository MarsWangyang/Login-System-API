"""create posts table

Revision ID: 8e8346cbd8ec
Revises: 
Create Date: 2022-06-15 21:47:40.225844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e8346cbd8ec'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 對下一次的databse做更改，就在這邊執行
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable=False,
                    primary_key=True), sa.Column('title', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    # 如果不想要此次的db schema，那麼就可以在這邊做修改，rollback to the last version
    op.drop_table('posts')
    pass
