"""add user table

Revision ID: 91453c16eab6
Revises: 2415fb9dc0e7
Create Date: 2022-06-15 23:21:07.997521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91453c16eab6'
down_revision = '2415fb9dc0e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String, nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
