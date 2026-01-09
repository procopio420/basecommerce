# Guia de Setup Inicial

## 1. Configuracao do Ambiente

### Vertical Construction

1. Entre no diretorio da vertical:
```bash
cd apps/verticals/construction
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
```

3. Instale as dependencias:
```bash
pip install -r requirements.txt

# Instale os pacotes compartilhados
pip install -e ../../../packages/basecore
pip install -e ../../../packages/engines_core
```

4. Configure as variaveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configuracoes:
# - DATABASE_URL
# - SECRET_KEY (gere uma chave aleatoria)
# - REDIS_URL
```

## 2. Configuracao do Banco de Dados e Redis

### Opcao A: Docker (Recomendado)

1. Use docker-compose para subir o PostgreSQL e Redis:
```bash
# Na raiz do projeto
docker-compose up -d db redis
```

### Opcao B: PostgreSQL e Redis Local

1. Instale o PostgreSQL 15+ e Redis 7+
2. Crie um banco de dados:
```sql
CREATE DATABASE basecommerce_db;
CREATE USER basecommerce_user WITH PASSWORD 'basecommerce_pass';
GRANT ALL PRIVILEGES ON DATABASE basecommerce_db TO basecommerce_user;
```

3. Configure as variaveis no .env:
```
DATABASE_URL=postgresql://basecommerce_user:basecommerce_pass@localhost:5432/basecommerce_db
REDIS_URL=redis://localhost:6379/0
```

## 3. Executar Migracoes

1. No diretorio da vertical:
```bash
cd apps/verticals/construction
PYTHONPATH=src alembic upgrade head
```

Isso criara todas as tabelas necessarias no banco de dados.

## 4. Criar Primeiro Tenant e Usuario

Execute o script para criar tenant, branding e usuario inicial:

```bash
cd apps/verticals/construction
PYTHONPATH=src python -c "
from sqlalchemy.orm import Session
from construction_app.core.database import SessionLocal
from construction_app.core.security import get_password_hash
from construction_app.models.tenant import Tenant
from construction_app.models.tenant_branding import TenantBranding
from construction_app.models.user import User

db = SessionLocal()

# Criar tenant com slug (usado no subdominio)
tenant = Tenant(
    nome='Loja Exemplo',
    slug='exemplo',  # Para dev local, acesse via exemplo.localhost:8000
    cnpj='12.345.678/0001-90',
    email='loja@exemplo.com',
    telefone='(24) 1234-5678',
    ativo=True
)
db.add(tenant)
db.commit()
db.refresh(tenant)

# Criar branding personalizado (opcional)
branding = TenantBranding(
    tenant_id=tenant.id,
    logo_url=None,  # URL do logo ou None
    primary_color='#1a73e8',
    secondary_color='#ea4335',
    feature_flags={}
)
db.add(branding)
db.commit()

# Criar usuario admin
user = User(
    tenant_id=tenant.id,
    nome='Administrador',
    email='admin@exemplo.com',
    password_hash=get_password_hash('senha123'),
    role='admin',
    ativo=True
)
db.add(user)
db.commit()

print(f'Tenant criado: {tenant.nome} (slug: {tenant.slug})')
print(f'Usuario criado: {user.email}')
print(f'Senha: senha123')
"
```

## 5. Iniciar Servidor

```bash
cd apps/verticals/construction
PYTHONPATH=src uvicorn construction_app.main:app --reload
```

O servidor estara disponivel em: http://localhost:8000

## 6. Primeiro Acesso

### Desenvolvimento Local

Para desenvolvimento local, voce pode acessar diretamente:
- http://localhost:8000/web/login

O sistema funciona sem subdominio em modo de desenvolvimento.

### Com Subdominio (Opcional)

Para testar com subdominio local, adicione ao `/etc/hosts`:
```
127.0.0.1 exemplo.localhost
```

E acesse:
- http://exemplo.localhost:8000/web/login

### Credenciais

Faca login com:
- Email: admin@exemplo.com
- Senha: senha123

## 7. Proximos Passos

1. **Dashboard**: Veja o resumo de cotacoes e pedidos
2. **Cotacoes**: Gerencie cotacoes (enviar, aprovar, cancelar)
3. **Pedidos**: Acompanhe pedidos criados a partir de cotacoes

## Troubleshooting

### Erro de Conexao com Banco de Dados

- Verifique se o PostgreSQL esta rodando
- Verifique se a DATABASE_URL esta correta
- Verifique se o usuario tem permissoes

### Erro de Conexao com Redis

- Verifique se o Redis esta rodando
- Verifique se a REDIS_URL esta correta

### Erro de Migracoes

- Certifique-se de que o banco esta vazio ou que voce esta usando um banco de teste
- Verifique se todas as dependencias estao instaladas

### Erro de Autenticacao

- Verifique se o SECRET_KEY esta configurado
- Verifique se o cookie `access_token` esta sendo enviado
- Em producao, verifique se cookies `secure` e HTTPS estao configurados

### Tenant Nao Encontrado

- Verifique se o tenant existe com o slug correto
- Verifique se o tenant esta ativo (`ativo=True`)
- Para dev local sem subdominio, o sistema funciona normalmente

### Erro de Import (ModuleNotFoundError)

- Certifique-se de que o PYTHONPATH inclui o diretorio `src`:
```bash
export PYTHONPATH=src
# ou
PYTHONPATH=src uvicorn construction_app.main:app --reload
```
