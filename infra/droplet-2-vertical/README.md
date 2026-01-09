# Droplet 2 - Construction Vertical

**Spec:** 1GB RAM, 1 vCPU, 25GB SSD (~$6/mo)

This droplet contains the Construction vertical application:
- FastAPI with Gunicorn (2 workers)
- HTMX server-side rendered frontend
- REST API for the construction domain

## Prerequisites

- Docker and Docker Compose installed
- Droplet 3 (infra) running and accessible
- Private networking enabled between droplets
- UFW configured (see Security section)

## Quick Start

```bash
# 1. Copy environment file
cp env.example .env

# 2. Edit .env with:
#    - INFRA_HOST = Droplet 3 private IP
#    - POSTGRES_PASSWORD = same as Droplet 3
#    - SECRET_KEY = generate new random key
nano .env

# 3. Bootstrap (first time only)
./scripts/bootstrap.sh

# 4. Start services
docker compose up -d

# 5. Verify health
./scripts/smoke-test.sh
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Construction | 8000 | FastAPI application |

## Memory Allocation (1GB total)

| Component | Allocation |
|-----------|------------|
| Gunicorn | ~768MB limit (2 workers × ~300MB each) |
| System | ~256MB reserved |

## Configuration

### Gunicorn Settings

- **Workers:** 2 (formula: 2 × vCPU + 1, but limited by RAM)
- **Threads:** 1 (sync workers for simpler debugging)
- **Timeout:** 60s (increase for slow queries)

### SQLAlchemy Pool

- **Pool Size:** 5 (connections kept open)
- **Max Overflow:** 10 (temporary connections)
- **Total Max:** 15 connections to PostgreSQL

## Security

### UFW Rules

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP from Droplet 1 only
sudo ufw allow from DROPLET_1_IP to any port 8000

# Enable firewall
sudo ufw enable
```

### Network Isolation

- Port 8000 is NOT exposed to public internet
- Only accessible from Droplet 1 (Edge) via private network

## Monitoring

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f construction

# Memory usage
docker stats basecommerce-construction

# Check Gunicorn workers
docker exec basecommerce-construction ps aux
```

## Deployments

```bash
# Standard update
./scripts/update.sh

# Force rebuild
docker compose build --no-cache
docker compose up -d
```

## Database Migrations

Migrations are run from this droplet since it has access to PostgreSQL:

```bash
# Enter container
docker exec -it basecommerce-construction bash

# Run migrations
cd /app
alembic upgrade head
```

## Scaling Notes

When approaching limits:
1. **Memory pressure**: Reduce GUNICORN_WORKERS to 1, or upgrade to 2GB droplet
2. **CPU bottleneck**: Upgrade to 2 vCPU droplet
3. **Connection pool exhausted**: Increase SQLALCHEMY_POOL_SIZE (also increase PostgreSQL max_connections)

## Troubleshooting

### Application won't start
```bash
docker compose logs construction
# Check if Droplet 3 is reachable
curl http://${INFRA_HOST}:5432  # Should refuse connection (postgres)
```

### Database connection errors
```bash
# Test connectivity
docker exec basecommerce-construction python -c "
from sqlalchemy import create_engine
import os
e = create_engine(os.environ['DATABASE_URL'])
with e.connect() as c:
    print('OK')
"
```

### OOM Killer
```bash
# Check if container was killed
docker inspect basecommerce-construction | grep -i oom
# Reduce workers or upgrade droplet
```

