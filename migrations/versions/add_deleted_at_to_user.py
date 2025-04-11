"""add deleted_at to user

Revision ID: add_deleted_at_to_user
Revises: allow_null_seller_id_v3
Create Date: 2024-03-05 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_deleted_at_to_user'
down_revision = 'allow_null_seller_id_v3'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna deleted_at na tabela user
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # Criar índice para melhorar performance de consultas
    op.create_index('ix_user_deleted_at', 'user', ['deleted_at'])


def downgrade():
    # Remover índice e coluna
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_deleted_at')
        batch_op.drop_column('deleted_at')