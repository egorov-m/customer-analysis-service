"""comment_sentiment_analysis migration

Revision ID: 3b598d3ee4cb
Revises: 2c80840f0e46
Create Date: 2023-07-08 00:14:22.097714

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b598d3ee4cb'
down_revision = '2c80840f0e46'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comment_sentiment_analysis',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('datetime_formation', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('comment_id', sa.Integer(), nullable=False),
    sa.Column('sentiment_value', sa.Float(), nullable=False),
    sa.Column('version_mark', sqlmodel.sql.sqltypes.AutoString(length=5), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('review_sentiment_analysis', 'sentiment_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('review_sentiment_analysis', 'sentiment_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.drop_table('comment_sentiment_analysis')
    # ### end Alembic commands ###
