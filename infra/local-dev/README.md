# Local Development Environment

Simulates the 3-droplet production setup on your local machine.

## Quick Start

```bash
# Start all services
docker compose up -d

# Run smoke test
./smoke-test.sh

# View logs
docker compose logs -f
```

## Access

| URL | Description |
|-----|-------------|
| http://localhost/docs | OpenAPI documentation |
| http://localhost/health | Health check |
| http://demo.localhost/web/dashboard | Demo tenant dashboard |
| http://demo.localhost/tenant.json | Tenant configuration |

**Note:** For subdomain routing to work locally, you may need to add entries to `/etc/hosts`:

```
127.0.0.1 demo.localhost
127.0.0.1 test.localhost
```

Or use a browser that supports `.localhost` subdomains (Chrome, Firefox do by default).

## Services

```
┌─────────────────────────────────────────────────────┐
│                   localhost:80                       │
│                     (nginx)                          │
│                        │                             │
│         ┌──────────────┼──────────────┐             │
│         ▼              ▼              ▼             │
│    /auth/*        /api/*         /web/*            │
│       │              │              │               │
│       ▼              ▼              ▼               │
│     auth:8001    construction:8000                  │
│                        │                             │
│              ┌─────────┴─────────┐                  │
│              ▼                   ▼                  │
│         postgres:5432       redis:6379              │
│              ▲                   ▲                  │
│              │                   │                  │
│       outbox-relay        engines-worker            │
└─────────────────────────────────────────────────────┘
```

## Common Commands

```bash
# Rebuild after code changes
docker compose build
docker compose up -d

# Database access
docker exec -it local-postgres psql -U basecommerce

# Redis access
docker exec -it local-redis redis-cli

# View specific service logs
docker compose logs -f construction
docker compose logs -f nginx

# Stop everything
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## Adding Test Tenants

Create a JSON file in `nginx/tenants/`:

```bash
cat > nginx/tenants/teste.json << 'EOF'
{
  "slug": "teste",
  "name": "Tenant de Teste",
  "theme": {
    "primaryColor": "#dc2626",
    "secondaryColor": "#b91c1c"
  },
  "features": {
    "cotacoes": true,
    "pedidos": true,
    "estoque": true,
    "fornecedores": true
  }
}
EOF

# Restart nginx to pick up changes
docker compose restart nginx
```

Access at: http://teste.localhost/web/dashboard

## Troubleshooting

### Port already in use
```bash
# Check what's using the port
lsof -i :80
lsof -i :5432
lsof -i :6379

# Stop conflicting services or change ports in docker-compose.yml
```

### Database connection errors
```bash
# Check if postgres is healthy
docker compose ps postgres
docker compose logs postgres
```

### Nginx 502 errors
```bash
# Check if upstream services are running
docker compose ps construction auth
docker compose logs construction
```

### Subdomains not working
Add to `/etc/hosts`:
```
127.0.0.1 demo.localhost test.localhost
```

Or access directly with Host header:
```bash
curl -H "Host: demo.localhost" http://localhost/tenant.json
```

