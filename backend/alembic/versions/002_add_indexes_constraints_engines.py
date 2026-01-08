"""add indexes and constraints for engines tables

Revision ID: 002_add_indexes_constraints
Revises: 001_add_estoque_fornecedores
Create Date: 2026-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_indexes_constraints'
down_revision = '001_add_estoque_fornecedores'
branch_labels = None
depends_on = None


def upgrade():
    # ===== ESTOQUE =====
    
    # Índice em produto_id para joins com produtos
    op.create_index('idx_estoque_produto', 'estoque', ['produto_id'])
    
    # Índice composto para queries de alertas (tenant + quantidade)
    op.create_index(
        'idx_estoque_tenant_quantidade',
        'estoque',
        ['tenant_id', 'quantidade_atual']
    )
    
    # Constraint check: quantidade_atual >= 0
    op.create_check_constraint(
        'ck_estoque_quantidade_nao_negativa',
        'estoque',
        'quantidade_atual >= 0'
    )
    
    # ===== FORNECEDOR_PRECOS =====
    
    # Índice em created_at para queries de histórico/tendência
    op.create_index('idx_fornecedor_precos_created_at', 'fornecedor_precos', ['created_at'])
    
    # Índice composto para comparações e alertas
    op.create_index(
        'idx_fornecedor_precos_tenant_produto_valido_created',
        'fornecedor_precos',
        ['tenant_id', 'produto_id', 'valido', 'created_at']
    )
    
    # Constraint check: preco > 0
    op.create_check_constraint(
        'ck_fornecedor_precos_preco_positivo',
        'fornecedor_precos',
        'preco > 0'
    )


def downgrade():
    # Remover constraints
    op.drop_constraint('ck_fornecedor_precos_preco_positivo', 'fornecedor_precos', type_='check')
    op.drop_constraint('ck_estoque_quantidade_nao_negativa', 'estoque', type_='check')
    
    # Remover índices
    op.drop_index('idx_fornecedor_precos_tenant_produto_valido_created', table_name='fornecedor_precos')
    op.drop_index('idx_fornecedor_precos_created_at', table_name='fornecedor_precos')
    
    op.drop_index('idx_estoque_tenant_quantidade', table_name='estoque')
    op.drop_index('idx_estoque_produto', table_name='estoque')

