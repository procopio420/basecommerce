# BaseCommerce

Plataforma SaaS multi-tenant para verticais de comercio.

## Inicio Rapido

```bash
docker-compose up -d
docker-compose exec construction alembic upgrade head
open http://localhost/web/login
```

## Estrutura

```
basecommerce/
├── apps/
│   ├── engines/              # Worker de eventos
│   ├── outbox-relay/         # Relay DB → Redis
│   └── verticals/
│       └── construction/     # Vertical de materiais
├── packages/
│   ├── basecore/            # Infra compartilhada
│   └── engines_core/        # Logica dos engines
├── infra/nginx/             # Multi-tenant config
└── docs/                    # Documentacao
```

## Documentacao

**Tecnico** (numerado):
- [01-overview](docs/01-overview.md)
- [02-architecture](docs/02-architecture.md)
- [03-infrastructure](docs/03-infrastructure.md)
- [04-dev-setup](docs/04-dev-setup.md)
- [05-deploy](docs/05-deploy.md)
- [06-multi-tenant](docs/06-multi-tenant.md)
- [07-events-engines](docs/07-events-engines.md)
- [08-scalability](docs/08-scalability.md)

**Produto**: [docs/product/](docs/product/)

**Engines**: [docs/engine/](docs/engine/)

**Referencia**: [docs/ref/](docs/ref/)

## Stack

Python 3.11 · FastAPI · HTMX · PostgreSQL · Redis Streams · Nginx · VPS
