"""add content column to posts table

Revision ID: 2415fb9dc0e7
Revises: 8e8346cbd8ec
Create Date: 2022-06-15 23:17:33.966754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2415fb9dc0e7'
down_revision = '8e8346cbd8ec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts',
                  sa.Column('content', sa.String, nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
