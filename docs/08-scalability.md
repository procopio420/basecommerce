# Analise de Escalabilidade

## Premissas

- **Ate 1000 tenants** (lojas de materiais de construcao)
- **Concentracao geografica**: Brasil, Sul Fluminense inicialmente
- **Trafego**: Baixo a medio por tenant (5-50 usuarios ativos por loja)
- **Uso intenso de eventos assincrono**
- **VPS-only**: DigitalOcean droplets, sem Kubernetes

## Pergunta Principal

> **Essa arquitetura aguenta 1000 clientes?**

**Resposta: SIM**, com folga para a maioria dos cenarios. Veja analise detalhada abaixo.

---

## Analise por Componente

### 1. Nginx (Reverse Proxy)

**Capacidade**: Um unico Nginx pode lidar com **10.000+ requests/segundo**.

**Para 1000 tenants**:
- Assumindo 50 usuarios ativos por tenant = 50.000 usuarios
- Assumindo 1 request a cada 10 segundos por usuario = 5.000 req/s (pico)
- Nginx lida tranquilamente

**Droplets necessarios**: 1 (pode estar no mesmo droplet que a vertical)

**Gargalo**: NAO

### 2. Vertical Construction (FastAPI)

**Capacidade**:
- FastAPI e async, muito eficiente
- Um droplet 4GB pode lidar com **500-1000 requests/segundo**

**Para 1000 tenants**:
- Trafego estimado: 500-2000 req/s em pico
- 1 droplet 4GB lida com isso

**Quando escalar horizontalmente**:
- Se resposta media > 200ms consistentemente
- Se CPU > 80% por periodos prolongados

**Droplets necessarios**: 1 (ate ~500 tenants), 2-3 (1000 tenants com margem)

**Gargalo**: BAIXO RISCO

### 3. Engines Worker (Redis Streams Consumer)

**Capacidade**:
- Processamento assincrono, nao afeta latencia do usuario
- Um worker processa **100-500 eventos/segundo**

**Para 1000 tenants**:
- Eventos estimados: ~10.000-50.000 eventos/dia
- = ~0.5-2 eventos/segundo (media)
- Picos: talvez 10-20 eventos/segundo
- 1 worker lida tranquilamente

**Quando escalar**:
- Se backlog de eventos > 10.000 pendentes
- Se delay de processamento > 5 minutos

**Droplets necessarios**: 1 (compartilhado ou dedicado 2GB)

**Gargalo**: NAO

### 4. Redis Streams (Event Bus)

**Capacidade**:
- Redis Streams pode lidar com **100.000+ mensagens/segundo**
- Memoria: ~100 bytes por evento

**Para 1000 tenants**:
- 50.000 eventos/dia = ~5MB/dia de memoria (sem retencao longa)
- Droplet 1GB de Redis e mais que suficiente

**Gargalo**: NAO

### 5. PostgreSQL (Banco de Dados)

**Capacidade**:
- Depende de queries e indices
- Droplet 4-8GB pode lidar com **1000-5000 queries/segundo** (queries simples)

**Para 1000 tenants**:
- Queries simples com indice em `tenant_id`: muito rapidas
- Todos os filtros por tenant_id estao indexados

**Indices criticos**:
```sql
CREATE INDEX idx_cotacoes_tenant_status ON cotacoes(tenant_id, status);
CREATE INDEX idx_pedidos_tenant_status ON pedidos(tenant_id, status);
CREATE INDEX idx_clientes_tenant ON clientes(tenant_id);
```

**Quando escalar**:
- Se tempo de query > 100ms consistentemente
- Se conexoes ativas > 100 por muito tempo
- Se disco > 80%

**Droplets necessarios**: 1 managed database (4-8GB) ou droplet dedicado

**Gargalo**: MEDIO RISCO (mais provavel ponto de atencao)

### 6. Auth

**Situacao atual**: Auth integrado na vertical (JWT)

**Para 1000 tenants**:
- JWT e stateless, sem pressao no auth
- Validacao de token e local (decode apenas)

**Ponto unico de falha**: NAO (cada vertical valida seu proprio token)

**Gargalo**: NAO

---

## Resumo de Recursos Necessarios

### Configuracao Minima (ate 200 tenants)

| Componente | Droplet | RAM | Custo/mes (DO) |
|------------|---------|-----|----------------|
| Vertical + Nginx | 1 | 4GB | ~$24 |
| Engines + Relay | 1 | 2GB | ~$12 |
| PostgreSQL | Managed | 2GB | ~$25 |
| Redis | 1 | 1GB | ~$6 |
| **Total** | 3-4 | 9GB | **~$67** |

### Configuracao Recomendada (ate 500 tenants)

| Componente | Droplet | RAM | Custo/mes (DO) |
|------------|---------|-----|----------------|
| Vertical + Nginx | 1 | 4GB | ~$24 |
| Engines + Relay | 1 | 2GB | ~$12 |
| PostgreSQL | Managed | 4GB | ~$50 |
| Redis | 1 | 1GB | ~$6 |
| **Total** | 3-4 | 11GB | **~$92** |

### Configuracao para 1000 tenants

| Componente | Droplet | RAM | Custo/mes (DO) |
|------------|---------|-----|----------------|
| Nginx | 1 | 2GB | ~$12 |
| Vertical | 2 | 4GB cada | ~$48 |
| Engines | 1 | 2GB | ~$12 |
| Relay | 1 | 1GB | ~$6 |
| PostgreSQL | Managed | 8GB | ~$100 |
| Redis | 1 | 2GB | ~$12 |
| **Total** | 6-7 | ~25GB | **~$190** |

---

## Onde Quebra Primeiro?

**Ordem de pressao** (mais provavel para menos provavel):

1. **PostgreSQL** - Queries complexas ou volume de dados
2. **Vertical (FastAPI)** - Muitos requests simultaneos
3. **Engines Worker** - Backlog de eventos
4. **Redis** - Improvavel antes de 10.000 tenants
5. **Nginx** - Improvavel antes de 100.000 tenants

---

## O que Escalar Primeiro?

### Se PostgreSQL virar gargalo:
1. Adicionar read replicas
2. Aumentar RAM do managed database
3. Otimizar queries (EXPLAIN ANALYZE)
4. Considerar particao por tenant_id (improvavel necessario)

### Se Vertical virar gargalo:
1. Adicionar segundo droplet
2. Load balancer (Nginx upstream com multiplos backends)
3. Nao e necessario mudar codigo (stateless)

### Se Engines virarem gargalo:
1. Adicionar mais workers (mesmo consumer group)
2. Redis Streams suporta multiplos consumers nativamente
3. Basta iniciar mais instancias do worker

---

## O que NAO Precisa Ser Feito Agora

1. **Kubernetes** - Complexidade desnecessaria para < 5.000 tenants
2. **Sharding de banco** - Tenant_id index e suficiente
3. **CDC (Change Data Capture)** - Outbox pattern funciona bem
4. **Message broker externo** - Redis Streams e suficiente
5. **Service mesh** - Comunicacao direta e mais simples
6. **Cache distribuido** - Cache local ou Redis simples basta
7. **Multiplos bancos por tenant** - Isolamento por tenant_id e suficiente

---

## Metricas a Monitorar

### Alertas Criticos

| Metrica | Threshold | Acao |
|---------|-----------|------|
| Latencia P95 | > 500ms | Investigar |
| CPU Vertical | > 80% por 5min | Escalar |
| Conexoes DB | > 80 | Aumentar pool |
| Eventos pendentes | > 5000 | Adicionar worker |
| Disco DB | > 80% | Aumentar disco |

### Dashboards Recomendados

- Requests/segundo por endpoint
- Latencia P50/P95/P99
- Eventos processados/minuto
- Conexoes ativas no DB
- Uso de memoria por servico

---

## Conclusao

**A arquitetura atual suporta 1000 clientes com folga.**

- Custos de infra: ~$100-200/mes
- Sem necessidade de Kubernetes
- Sem necessidade de sharding
- Escalamento horizontal simples quando necessario

**Primeiro ponto de atencao**: PostgreSQL (monitorar queries e indices)

**Quando repensar arquitetura**: > 5.000 tenants ou casos de uso muito diferentes

