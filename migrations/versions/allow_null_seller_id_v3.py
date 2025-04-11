"""allow null seller id v3

Revision ID: allow_null_seller_id_v3
Revises: 14739f746960
Create Date: 2024-03-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'allow_null_seller_id_v3'
down_revision = '14739f746960'
branch_labels = None
depends_on = None


def upgrade():
    # Alterar a coluna para permitir valores nulos
    with op.batch_alter_table('sale') as batch_op:
        # Primeiro, remover qualquer restrição de chave estrangeira existente
        batch_op.drop_constraint('fk_sale_seller_id_user', type_='foreignkey')
        
        # Alterar a coluna para permitir valores nulos
        batch_op.alter_column('seller_id',
                    existing_type=sa.Integer(),
                    nullable=True,
                    existing_server_default=None)


def downgrade():
    # Reverter as alterações
    with op.batch_alter_table('sale') as batch_op:
        # Primeiro, garantir que não existam valores nulos
        op.execute('UPDATE sale SET seller_id = 1 WHERE seller_id IS NULL')
        
        # Alterar a coluna para não permitir valores nulos
        batch_op.alter_column('seller_id',
                    existing_type=sa.Integer(),
                    nullable=False,
                    existing_server_default=None)
        
        # Recriar a restrição de chave estrangeira
        batch_op.create_foreign_key(
            'fk_sale_seller_id_user',
            'user',
            ['seller_id'],
            ['id']
        )