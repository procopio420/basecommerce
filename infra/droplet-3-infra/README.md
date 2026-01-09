# Droplet 3 - Shared Infrastructure

**Spec:** 2GB RAM, 1 vCPU, 50GB SSD (~$12/mo)

This droplet contains all shared infrastructure services:
- PostgreSQL 16 (primary database)
- Redis 7 (event streams)
- Outbox Relay (DB → Redis)
- Engines Worker (event processing)

## Prerequisites

- Docker and Docker Compose installed
- UFW configured (see Security section)
- Private networking enabled between droplets

## Quick Start

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with secure passwords
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
| PostgreSQL | 5432 | Multi-tenant database |
| Redis | 6379 | Event streams (Redis Streams) |
| Outbox Relay | - | Polls outbox table → publishes to Redis |
| Engines Worker | - | Consumes events → updates engine tables |

## Memory Allocation (2GB total)

| Component | Allocation |
|-----------|------------|
| PostgreSQL | ~1.5GB (shared_buffers=512MB + effective_cache) |
| Redis | 256MB (maxmemory) |
| Workers | ~256MB (Python processes) |

## Backups

```bash
# Manual backup
./scripts/backup-postgres.sh

# Restore from backup
./scripts/restore-postgres.sh backup-2024-01-01.sql.gz
```

Backups are stored in `./backups/` directory.

## Security

### UFW Rules

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow PostgreSQL from Droplet 2 only
sudo ufw allow from DROPLET_2_IP to any port 5432

# Allow Redis from Droplet 2 only
sudo ufw allow from DROPLET_2_IP to any port 6379

# Enable firewall
sudo ufw enable
```

### Network Isolation

- PostgreSQL and Redis are NOT exposed to public internet
- Only accessible from Droplet 2 via private network
- Docker network `infra-network` isolates containers

## Monitoring

```bash
# Check all services
docker compose ps

# PostgreSQL stats
docker exec basecommerce-postgres psql -U basecommerce -c "SELECT * FROM pg_stat_activity;"

# Redis info
docker exec basecommerce-redis redis-cli INFO

# View logs
docker compose logs -f
docker compose logs -f postgres
docker compose logs -f outbox-relay
```

## Scaling Notes

When approaching limits:
1. **PostgreSQL connections maxed**: Increase `max_connections` or add PgBouncer
2. **Redis memory full**: Trim old stream entries or increase `maxmemory`
3. **Disk full**: Clean old backups, increase droplet storage
4. **CPU bottleneck**: Scale to 2 vCPU droplet ($24/mo)

## Troubleshooting

### PostgreSQL won't start
```bash
docker compose logs postgres
# Check disk space
df -h
```

### Redis OOM
```bash
docker exec basecommerce-redis redis-cli INFO memory
# Consider trimming old stream entries
```

### Outbox Relay stuck
```bash
docker compose restart outbox-relay
docker compose logs outbox-relay
```

