"""review_sentiment_analysis migration

Revision ID: 2c80840f0e46
Revises: a489869a14f6
Create Date: 2023-07-07 23:49:51.883459

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2c80840f0e46'
down_revision = 'a489869a14f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('review_sentiment_analysis',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('datetime_formation', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('review_id', sa.Integer(), nullable=False),
    sa.Column('sentiment_value', sa.Float(), nullable=True),
    sa.Column('version_mark', sqlmodel.sql.sqltypes.AutoString(length=5), nullable=False),
    sa.PrimaryKeyConstraint('id', 'review_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review_sentiment_analysis')
    # ### end Alembic commands ###
