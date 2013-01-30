"""create torrent table

Revision ID: 3a32ea1fc997
Revises: None
Create Date: 2013-01-27 16:02:24.863403

"""

# revision identifiers, used by Alembic.
revision = '3a32ea1fc997'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'torrent',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('info_hash', sa.String(40), nullable=False),
        sa.Column('state', sa.String(16)),
    )


def downgrade():
    op.drop_table('torrent')
