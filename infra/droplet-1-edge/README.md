# Droplet 1 - Edge (Nginx)

**Spec:** 1GB RAM, 1 vCPU, 25GB SSD (~$6/mo)

This droplet is the public-facing edge:
- Nginx reverse proxy (multi-tenant routing)
- Auth service placeholder
- Rate limiting and security headers

## Architecture

```
Internet → Cloudflare (TLS) → Droplet 1 (Nginx :80)
                                    │
                                    ├── /auth/* → Auth Service (:8001)
                                    ├── /tenant.json → Static JSON files
                                    └── /* → Droplet 2 (:8000)
```

## Prerequisites

- Docker and Docker Compose installed
- Droplet 2 and 3 running
- Cloudflare DNS configured (Full/Strict SSL)
- UFW configured (see Security section)

## Quick Start

```bash
# 1. Copy environment file
cp env.example .env

# 2. Edit .env with:
#    - VERTICAL_HOST = Droplet 2 private IP
#    - SECRET_KEY = generate new random key
nano .env

# 3. Update nginx config with Droplet 2 IP
#    Edit nginx/conf.d/default.conf and replace ${VERTICAL_HOST}
#    with actual IP (e.g., 10.0.0.2)
nano nginx/conf.d/default.conf

# 4. Bootstrap (first time only)
./scripts/bootstrap.sh

# 5. Start services
docker compose up -d

# 6. Verify health
./scripts/smoke-test.sh
```

## Multi-Tenant Routing

Nginx extracts the tenant from subdomain:

| Request | Tenant Slug |
|---------|-------------|
| `lojadoze.basecommerce.com.br` | `lojadoze` |
| `construmax.basecommerce.com.br` | `construmax` |
| `demo.localhost` | `demo` |
| `localhost` | `""` (empty) |

The tenant slug is passed to upstream services via `X-Tenant-Slug` header.

## Tenant Configuration

Add new tenants by creating JSON files in `nginx/tenants/`:

```bash
# Create new tenant config
cat > nginx/tenants/novotenant.json << EOF
{
  "slug": "novotenant",
  "name": "Novo Tenant",
  "theme": {
    "primaryColor": "#2563eb",
    "secondaryColor": "#1e40af",
    "logoUrl": null
  },
  "features": {
    "cotacoes": true,
    "pedidos": true,
    "estoque": true,
    "fornecedores": true
  }
}
EOF

# Reload nginx
docker exec basecommerce-nginx nginx -s reload
```

## Security

### Cloudflare Setup

1. Add DNS A record: `*.basecommerce.com.br` → Droplet 1 public IP
2. Enable proxy (orange cloud)
3. SSL/TLS: Full (strict)
4. Enable DDoS protection

### UFW Rules

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP (Cloudflare will handle HTTPS)
sudo ufw allow 80/tcp

# Enable firewall
sudo ufw enable
```

### Rate Limiting

| Zone | Rate | Burst |
|------|------|-------|
| API | 10 req/s | 20 |
| Web | 30 req/s | 50 |
| Auth | 5 req/s | 10 |

## Monitoring

```bash
# Check services
docker compose ps

# Nginx status
curl http://localhost/nginx-status

# View access logs
docker compose logs -f nginx

# Real-time connections
docker exec basecommerce-nginx nginx -T | grep -E "(limit_|upstream)"
```

## Common Operations

### Reload Nginx config (no downtime)
```bash
docker exec basecommerce-nginx nginx -s reload
```

### Update tenant config
```bash
# Edit tenant file
nano nginx/tenants/cliente.json

# Reload nginx
docker exec basecommerce-nginx nginx -s reload
```

### Test nginx config
```bash
docker exec basecommerce-nginx nginx -t
```

## Troubleshooting

### 502 Bad Gateway
```bash
# Check if Droplet 2 is reachable
curl http://${VERTICAL_HOST}:8000/health

# Check nginx logs
docker compose logs nginx
```

### Tenant not found
```bash
# Check if tenant file exists
ls nginx/tenants/

# Check nginx config
docker exec basecommerce-nginx cat /etc/nginx/conf.d/default.conf
```

### Rate limiting too aggressive
```bash
# Check rate limit config
docker exec basecommerce-nginx nginx -T | grep limit_req

# Adjust in nginx/conf.d/default.conf and reload
```

