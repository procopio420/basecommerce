# Multi-Tenancy

## Estrategia

**Subdomain-based multi-tenancy** com dados isolados por `tenant_id` em todas as tabelas.

## Fluxo de Resolucao

```
1. Usuario acessa: lojadoze.basecommerce.com.br
                              │
                              ▼
2. Nginx extrai subdomain: lojadoze
                              │
                              ▼
3. Nginx injeta header: X-Tenant-Slug: lojadoze
                              │
                              ▼
4. Backend middleware le header (ou Host em dev)
                              │
                              ▼
5. Middleware busca tenant no banco por slug
                              │
                              ▼
6. request.state.tenant_id = tenant.id
                              │
                              ▼
7. Todas as queries filtram por tenant_id
```

## Configuracao Nginx

```nginx
# Extrai tenant do subdomain
map $host $tenant_slug {
    ~^(?<subdomain>[^.]+)\.basecommerce\.com\.br$ $subdomain;
    ~^(?<subdomain>[^.]+)\.localhost$ $subdomain;
    default "";
}

server {
    listen 80;
    server_name *.basecommerce.com.br *.localhost localhost;
    
    location / {
        proxy_pass http://construction:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Tenant-Slug $tenant_slug;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Middleware Python

```python
def get_tenant_slug_from_request(request: Request) -> str | None:
    # Prioridade 1: Header X-Tenant-Slug (producao, via Nginx)
    tenant_slug = request.headers.get("x-tenant-slug", "").strip()
    if tenant_slug:
        return tenant_slug
    
    # Prioridade 2: Parse do Host (desenvolvimento local)
    host = request.headers.get("host", "")
    return extract_slug_from_host(host)
```

## Tenant Branding

Cada tenant pode ter branding personalizado:

```sql
CREATE TABLE tenant_branding (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id),
    logo_url VARCHAR(500),
    primary_color VARCHAR(7) DEFAULT '#1a73e8',
    secondary_color VARCHAR(7) DEFAULT '#ea4335',
    feature_flags JSONB DEFAULT '{}'
);
```

O branding e injetado no contexto dos templates Jinja2:

```python
context = {
    "tenant_name": tenant.nome,
    "branding": {
        "primary_color": branding.primary_color,
        "logo_url": branding.logo_url,
    }
}
```

## Desenvolvimento Local

### Sem Subdomain

Acesse diretamente `http://localhost:8000/web/login`.
O sistema funciona sem tenant especifico (modo desenvolvimento).

### Com Subdomain

1. Adicione ao `/etc/hosts`:
```
127.0.0.1 exemplo.localhost
```

2. Acesse: `http://exemplo.localhost:8000/web/login`

O middleware resolve `exemplo` como slug e busca o tenant no banco.

## Isolamento de Dados

**TODAS** as queries de dados de negocio filtram por `tenant_id`:

```python
cotacoes = (
    db.query(Cotacao)
    .filter(Cotacao.tenant_id == tenant_id)  # OBRIGATORIO
    .order_by(Cotacao.created_at.desc())
    .all()
)
```

**Engines** tambem respeitam `tenant_id` nos eventos:

```python
envelope = EventEnvelope(
    event_id=uuid4(),
    event_type="sale_recorded",
    tenant_id=tenant_id,  # Sempre presente
    payload={...}
)
```

## Criacao de Novo Tenant

```python
# 1. Criar tenant
tenant = Tenant(
    nome="Nova Loja",
    slug="novaloja",  # Subdomain
    cnpj="12.345.678/0001-90",
    email="contato@novaloja.com",
    ativo=True
)
db.add(tenant)
db.commit()

# 2. Criar branding (opcional)
branding = TenantBranding(
    tenant_id=tenant.id,
    primary_color="#1a73e8"
)
db.add(branding)
db.commit()

# 3. Criar usuario admin
user = User(
    tenant_id=tenant.id,
    nome="Admin",
    email="admin@novaloja.com",
    password_hash=get_password_hash("senha123"),
    role="admin",
    ativo=True
)
db.add(user)
db.commit()
```

Apos isso, o tenant pode acessar via `novaloja.basecommerce.com.br`.

