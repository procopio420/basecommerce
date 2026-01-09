# Infraestrutura

## Visao Geral

A plataforma roda em VPS (DigitalOcean droplets) sem Kubernetes nem serverless.

## Componentes

### PostgreSQL

- Versao: 15+
- Multi-tenant: todas as tabelas tem `tenant_id`
- Pode ser managed (DO Managed Database) ou self-hosted

### Redis

- Versao: 7+
- Usos:
  - Redis Streams para eventos (event bus)
  - Cache de sessao (futuro)
- Append-only habilitado para persistencia

### Nginx

- Reverse proxy multi-tenant
- Resolve tenant via subdomain
- Injeta header `X-Tenant-Slug`
- Arquivo: `infra/nginx/nginx.conf`

### Droplets (Arquitetura de Deploy)

```
┌─────────────────┐     ┌─────────────────┐
│   Nginx         │     │   PostgreSQL    │
│   (1 droplet)   │     │   (1 droplet    │
│   ou integrado  │     │    ou managed)  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       │
┌─────────────────┐              │
│  Construction   │◄─────────────┘
│  Vertical       │              │
│  (1 droplet)    │◄─────────────┤
└────────┬────────┘              │
         │                       │
         ▼                       │
┌─────────────────┐              │
│  Engines Worker │◄─────────────┘
│  (1 droplet     │
│   ou no mesmo)  │
└─────────────────┘
```

## Configuracao Minima (Desenvolvimento)

Um unico droplet pode rodar todos os servicos:

```bash
docker-compose up -d
```

Isso inicia:
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- Nginx (porta 80)
- Construction vertical (porta 8000)
- Outbox Relay
- Engines Worker

## Configuracao Producao

### Droplet para Vertical (4GB+ RAM)

```bash
docker run -d -p 8000:8000 \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  -e SECRET_KEY=... \
  basecommerce-construction
```

### Droplet para Engines (2GB+ RAM)

```bash
docker run -d \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  -e SECRET_KEY=... \
  basecommerce-engines
```

### Nginx (No droplet da vertical ou separado)

Veja `infra/nginx/nginx.conf` para configuracao completa.

## Variaveis de Ambiente

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| DATABASE_URL | Connection string PostgreSQL | postgresql://user:pass@host:5432/db |
| REDIS_URL | Connection string Redis | redis://host:6379/0 |
| SECRET_KEY | Chave para JWT | (gerar aleatoriamente) |
| ALGORITHM | Algoritmo JWT | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Expiracao do token | 1440 |
| CORS_ORIGINS | Origins permitidos | http://localhost |

## Monitoramento

### Logs

- Vertical: stdout do container (docker logs)
- Nginx: `/var/log/nginx/access.log` e `error.log`
- PostgreSQL: logs do container ou managed

### Health Checks

- Vertical: `GET /health` → `{"status": "ok"}`
- Engines: logs de processamento de eventos

### Metricas (Futuro)

- Prometheus + Grafana
- Metricas de eventos processados
- Tempo de resposta de endpoints

