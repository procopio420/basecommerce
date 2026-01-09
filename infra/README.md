# BaseCommerce Infrastructure

Infrastructure as Code for the BaseCommerce platform.

## Overview

The platform runs on 3 DigitalOcean droplets with a total cost of ~$24/month:

| Droplet | Purpose | Spec | Cost |
|---------|---------|------|------|
| **Edge** | Nginx + Auth | 1GB, 1vCPU | $6/mo |
| **Vertical** | Construction app | 1GB, 1vCPU | $6/mo |
| **Infra** | PostgreSQL + Redis + Workers | 2GB, 1vCPU | $12/mo |

## Architecture

```
                         INTERNET
                            │
                            ▼
                    ┌───────────────┐
                    │   CLOUDFLARE  │
                    │   (TLS/CDN)   │
                    └───────┬───────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    DROPLET 1 - EDGE                           │
│                                                               │
│   ┌─────────────┐        ┌─────────────┐                     │
│   │    Nginx    │───────▶│    Auth     │                     │
│   │    (:80)    │        │   (:8001)   │                     │
│   └──────┬──────┘        └─────────────┘                     │
│          │                                                    │
│          │ X-Tenant-Slug header                              │
└──────────┼────────────────────────────────────────────────────┘
           │
           ▼
┌───────────────────────────────────────────────────────────────┐
│                  DROPLET 2 - VERTICAL                         │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐    │
│   │              Construction App                        │    │
│   │              FastAPI + HTMX                         │    │
│   │              (:8000)                                │    │
│   └─────────────────────────┬───────────────────────────┘    │
│                             │                                 │
└─────────────────────────────┼─────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│                   DROPLET 3 - INFRA                           │
│                                                               │
│   ┌──────────────┐    ┌──────────────┐                       │
│   │  PostgreSQL  │    │    Redis     │                       │
│   │   (:5432)    │    │   (:6379)    │                       │
│   └──────┬───────┘    └──────┬───────┘                       │
│          │                   │                                │
│          │    ┌──────────────┼──────────────┐                │
│          │    │              │              │                │
│          ▼    ▼              ▼              ▼                │
│   ┌─────────────────┐  ┌─────────────────────┐              │
│   │  Outbox Relay   │  │   Engines Worker    │              │
│   └─────────────────┘  └─────────────────────┘              │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
infra/
├── README.md                  # This file
├── topology.md                # Detailed architecture decisions
│
├── droplet-1-edge/            # Nginx + Auth
│   ├── docker-compose.yml
│   ├── nginx/
│   │   ├── nginx.conf
│   │   ├── conf.d/default.conf
│   │   └── tenants/*.json
│   ├── env.example
│   └── scripts/
│       ├── bootstrap.sh
│       ├── update.sh
│       └── smoke-test.sh
│
├── droplet-2-vertical/        # Construction App
│   ├── docker-compose.yml
│   ├── env.example
│   └── scripts/
│       ├── bootstrap.sh
│       ├── update.sh
│       └── smoke-test.sh
│
├── droplet-3-infra/           # PostgreSQL + Redis + Workers
│   ├── docker-compose.yml
│   ├── postgres/postgresql.conf
│   ├── redis/redis.conf
│   ├── env.example
│   └── scripts/
│       ├── bootstrap.sh
│       ├── update.sh
│       ├── backup-postgres.sh
│       ├── restore-postgres.sh
│       └── smoke-test.sh
│
└── local-dev/                 # Local development (simulates 3 droplets)
    ├── docker-compose.yml
    ├── nginx/
    └── smoke-test.sh
```

## Deployment Order

Always deploy in this order:

1. **Droplet 3 (Infra)** - Database and Redis must be available first
2. **Droplet 2 (Vertical)** - Connects to Droplet 3
3. **Droplet 1 (Edge)** - Routes traffic to Droplet 2

## Quick Deploy Guide

### Prerequisites

1. Create 3 DigitalOcean droplets with private networking enabled
2. Configure Cloudflare DNS:
   - A record: `*.basecommerce.com.br` → Droplet 1 public IP
   - SSL mode: Full (strict)

### Droplet 3 (Infra)

```bash
# SSH into droplet
ssh root@DROPLET_3_IP

# Clone repo
git clone https://github.com/yourrepo/basecommerce.git
cd basecommerce/infra/droplet-3-infra

# Run bootstrap as root
sudo ./scripts/bootstrap.sh

# Configure and start
cp env.example .env
nano .env  # Set POSTGRES_PASSWORD
docker compose up -d
./scripts/smoke-test.sh
```

### Droplet 2 (Vertical)

```bash
ssh root@DROPLET_2_IP

git clone https://github.com/yourrepo/basecommerce.git
cd basecommerce/infra/droplet-2-vertical

sudo ./scripts/bootstrap.sh

cp env.example .env
nano .env  # Set INFRA_HOST, POSTGRES_PASSWORD, SECRET_KEY
docker compose up -d
./scripts/smoke-test.sh
```

### Droplet 1 (Edge)

```bash
ssh root@DROPLET_1_IP

git clone https://github.com/yourrepo/basecommerce.git
cd basecommerce/infra/droplet-1-edge

sudo ./scripts/bootstrap.sh

cp env.example .env
nano .env  # Set VERTICAL_HOST, SECRET_KEY

# Update nginx config with actual IP
sed -i 's/${VERTICAL_HOST}/10.0.0.2/g' nginx/conf.d/default.conf

docker compose up -d
./scripts/smoke-test.sh
```

## Security

### Firewall (UFW)

| Droplet | Open Ports |
|---------|------------|
| Edge | 22 (SSH), 80 (HTTP) |
| Vertical | 22 (SSH), 8000 (internal only) |
| Infra | 22 (SSH), 5432 + 6379 (internal only) |

### Network Isolation

- Use DigitalOcean VPC for internal communication
- Only Droplet 1 (Edge) is publicly accessible
- All internal traffic uses private IPs

### TLS

- Cloudflare handles TLS termination
- Internal traffic between droplets is unencrypted (VPC)
- Consider Tailscale/WireGuard for additional security

## Monitoring

```bash
# On each droplet
docker compose ps
docker stats
docker compose logs -f
```

## Backups

Backups are automated on Droplet 3:

```bash
# Manual backup
./scripts/backup-postgres.sh

# Restore
./scripts/restore-postgres.sh backup-2024-01-01.sql.gz
```

Backups are stored in `./backups/` with 7-day retention.

## Scaling

See [topology.md](topology.md) for detailed scaling guidance.

| Bottleneck | Solution |
|------------|----------|
| Database connections | Add PgBouncer |
| Database performance | Upgrade Droplet 3 to 4GB |
| Web traffic | Add second Edge droplet + load balancer |
| Background processing | Add second Engines Worker |

## Local Development

```bash
cd infra/local-dev
docker compose up -d
./smoke-test.sh

# Access
open http://demo.localhost/web/dashboard
```

