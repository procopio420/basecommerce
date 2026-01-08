"""add estoque fornecedores tables

Revision ID: 001_add_estoque_fornecedores
Revises: 
Create Date: 2026-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_estoque_fornecedores'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela estoque
    op.create_table(
        'estoque',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('produto_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantidade_atual', sa.Numeric(10, 3), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ondelete='CASCADE'),
    )
    
    op.create_index('idx_estoque_tenant_produto', 'estoque', ['tenant_id', 'produto_id'], unique=True)
    op.create_index('idx_estoque_tenant', 'estoque', ['tenant_id'])
    
    # Criar tabela fornecedores
    op.create_table(
        'fornecedores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('documento', sa.String(20)),
        sa.Column('email', sa.String(255)),
        sa.Column('telefone', sa.String(20)),
        sa.Column('endereco', sa.Text()),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    
    op.create_index('idx_fornecedores_tenant_ativo', 'fornecedores', ['tenant_id', 'ativo'])
    op.create_index('idx_fornecedores_tenant_documento', 'fornecedores', ['tenant_id', 'documento'], unique=True)
    
    # Criar tabela fornecedor_precos
    op.create_table(
        'fornecedor_precos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fornecedor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('produto_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('preco', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantidade_minima', sa.Numeric(10, 3)),
        sa.Column('prazo_pagamento', sa.Numeric(5, 0)),
        sa.Column('valido', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fornecedor_id'], ['fornecedores.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ondelete='CASCADE'),
    )
    
    op.create_index('idx_fornecedor_precos_tenant_fornecedor_produto', 'fornecedor_precos', ['tenant_id', 'fornecedor_id', 'produto_id'])
    op.create_index('idx_fornecedor_precos_tenant_produto', 'fornecedor_precos', ['tenant_id', 'produto_id'])
    op.create_index('idx_fornecedor_precos_valido', 'fornecedor_precos', ['tenant_id', 'valido'])


def downgrade():
    # Remover índices e tabelas na ordem inversa
    op.drop_index('idx_fornecedor_precos_valido', table_name='fornecedor_precos')
    op.drop_index('idx_fornecedor_precos_tenant_produto', table_name='fornecedor_precos')
    op.drop_index('idx_fornecedor_precos_tenant_fornecedor_produto', table_name='fornecedor_precos')
    op.drop_table('fornecedor_precos')
    
    op.drop_index('idx_fornecedores_tenant_documento', table_name='fornecedores')
    op.drop_index('idx_fornecedores_tenant_ativo', table_name='fornecedores')
    op.drop_table('fornecedores')
    
    op.drop_index('idx_estoque_tenant', table_name='estoque')
    op.drop_index('idx_estoque_tenant_produto', table_name='estoque')
    op.drop_table('estoque')

