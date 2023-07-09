"""migration

Revision ID: f512b5e8c07b
Revises: 0b652122f657
Create Date: 2023-07-09 10:49:46.785851

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f512b5e8c07b'
down_revision = '0b652122f657'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('customer_similarity_analysis', 'similarity_reviews_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('customer_similarity_analysis', 'similarity_comments_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('product_similarity_analysis', 'similarity_reviews_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('product_similarity_analysis', 'similarity_comments_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product_similarity_analysis', 'similarity_comments_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('product_similarity_analysis', 'similarity_reviews_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('customer_similarity_analysis', 'similarity_comments_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('customer_similarity_analysis', 'similarity_reviews_value',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    # ### end Alembic commands ###
