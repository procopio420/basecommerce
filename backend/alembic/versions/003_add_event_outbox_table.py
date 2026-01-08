"""add event outbox table

Revision ID: 003_add_event_outbox
Revises: 002_add_indexes_constraints
Create Date: 2026-01-15 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_event_outbox'
down_revision = '002_add_indexes_constraints'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela event_outbox
    op.create_table(
        'event_outbox',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False, server_default='1.0'),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('event_id'),
    )
    
    # Criar índices
    op.create_index('idx_event_outbox_event_type', 'event_outbox', ['event_type'])
    op.create_index('idx_event_outbox_status', 'event_outbox', ['status'])
    op.create_index('idx_event_outbox_tenant_status', 'event_outbox', ['tenant_id', 'status'])
    op.create_index('idx_event_outbox_status_created', 'event_outbox', ['status', 'created_at'])


def downgrade():
    # Remover índices
    op.drop_index('idx_event_outbox_status_created', table_name='event_outbox')
    op.drop_index('idx_event_outbox_tenant_status', table_name='event_outbox')
    op.drop_index('idx_event_outbox_status', table_name='event_outbox')
    op.drop_index('idx_event_outbox_event_type', table_name='event_outbox')
    
    # Remover tabela
    op.drop_table('event_outbox')

