# Eventos e Engines

## Arquitetura Event-Driven

A plataforma usa **Outbox Pattern** para garantir entrega de eventos:

```
Vertical (write)
      │
      ▼
┌─────────────────┐
│  Mesma transacao │
│  - INSERT pedido │
│  - INSERT outbox │
│  COMMIT          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Outbox Relay    │
│  (polling DB)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Redis Streams   │
│  (event bus)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Engines Worker  │
│  (XREADGROUP)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Engine Tables   │
│  (engine-owned)  │
└─────────────────┘
```

## Publicando Eventos (Vertical)

```python
from construction_app.platform.events.publisher import publish_event

# Na mesma transacao do write principal
with db.begin():
    pedido = Pedido(...)
    db.add(pedido)
    
    publish_event(
        db=db,
        event_type="sale_recorded",
        tenant_id=tenant_id,
        payload={
            "pedido_id": str(pedido.id),
            "cliente_id": str(pedido.cliente_id),
            "itens": [...],
            "valor_total": float(pedido.valor_total),
        }
    )
    # COMMIT acontece aqui - ambos ou nenhum
```

## Consumindo Eventos (Engines)

O worker em `apps/engines/` consome eventos via Redis Streams:

```python
# engines_core/consumer.py

messages = read_from_stream(
    stream_name="events:materials",
    group_name="engines",
    consumer_name="engines-worker",
    count=10,
    block_ms=5000,
)

for msg_id, data in messages:
    envelope = parse_stream_message(msg_id, data)
    result = handle_event(db, envelope)  # Roteia para handler
    ack_message(stream_name, group_name, msg_id)
```

## Tipos de Eventos

| Evento | Quando | Payload |
|--------|--------|---------|
| `quote_created` | Cotacao criada | cotacao_id, cliente_id, itens |
| `quote_converted` | Cotacao → Pedido | cotacao_id, pedido_id |
| `sale_recorded` | Pedido criado | pedido_id, itens, valor |
| `order_delivered` | Pedido entregue | pedido_id, data_entrega |

## Engines Disponiveis

### Stock Intelligence

**Responsabilidade**: O QUE comprar, QUANDO comprar, QUANTO comprar

- Consome: `sale_recorded`, `order_delivered`
- Produz: Alertas de ruptura, sugestoes de reposicao
- Tabelas: `engine_stock_*`

### Sales Intelligence

**Responsabilidade**: Aumentar valor da venda

- Consome: `sale_recorded`, `quote_created`
- Produz: Sugestoes de produtos complementares
- Tabelas: `engine_sales_*`

### Pricing & Supplier Intelligence

**Responsabilidade**: DE QUEM comprar, A QUE CUSTO

- Consome: Eventos de fornecedor (futuro)
- Produz: Comparacao de fornecedores, custo base
- Tabelas: `engine_pricing_*`

### Delivery & Fulfillment

**Responsabilidade**: Pedido → Entrega → Confirmacao

- Consome: `order_delivered`
- Produz: Rotas, status, prova de entrega
- Tabelas: `engine_delivery_*`

## Idempotencia

Eventos sao processados de forma idempotente:

```sql
CREATE TABLE engine_processed_events (
    event_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    processed_at TIMESTAMP DEFAULT now(),
    result JSONB
);
```

Antes de processar:
```python
if is_event_processed(db, event_id):
    return  # Skip - ja processado

# Processa...

mark_event_processed(db, event_id, tenant_id, event_type, result)
```

## Regras de Isolamento

1. **Engines NAO importam verticais**
   ```python
   # ERRADO
   from construction_app.models import Pedido
   
   # CERTO
   from engines_core.contracts.envelope import EventEnvelope
   from basecore.db import get_db
   ```

2. **Engines usam apenas**:
   - `packages/basecore/` (db, redis, settings)
   - `packages/engines_core/` (handlers, contracts)

3. **Dados de engines em tabelas proprias**:
   - Prefixo `engine_*`
   - Nunca modificam tabelas de verticais

## Debugging

### Ver eventos pendentes

```sql
SELECT * FROM event_outbox 
WHERE status = 'pending' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Ver eventos processados por engines

```sql
SELECT * FROM engine_processed_events 
ORDER BY processed_at DESC 
LIMIT 10;
```

### Logs do worker

```bash
docker-compose logs -f engines-worker
```

