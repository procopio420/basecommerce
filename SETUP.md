# Guia de Setup Inicial

## 1. Configuração do Ambiente

### Backend

1. Entre no diretório do backend:
```bash
cd backend
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configurações:
# - DATABASE_URL
# - SECRET_KEY (gere uma chave aleatória)
# - CORS_ORIGINS
```

### Frontend

1. Entre no diretório do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Configure as variáveis de ambiente (opcional):
```bash
# Crie .env se necessário
VITE_API_URL=http://localhost:8000
```

## 2. Configuração do Banco de Dados

### Opção A: Docker (Recomendado)

1. Use docker-compose para subir o PostgreSQL:
```bash
docker-compose up -d db
```

### Opção B: PostgreSQL Local

1. Instale o PostgreSQL 15+
2. Crie um banco de dados:
```sql
CREATE DATABASE construcao_db;
CREATE USER construcao_user WITH PASSWORD 'construcao_pass';
GRANT ALL PRIVILEGES ON DATABASE construcao_db TO construcao_user;
```

3. Configure a DATABASE_URL no .env:
```
DATABASE_URL=postgresql://construcao_user:construcao_pass@localhost:5432/construcao_db
```

## 3. Executar Migrações

1. No diretório do backend:
```bash
cd backend
alembic upgrade head
```

Isso criará todas as tabelas necessárias no banco de dados.

## 4. Criar Primeiro Tenant e Usuário

Execute o script de setup (criar manualmente por enquanto):

```python
# scripts/create_initial_data.py (criar este arquivo)
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.user import User

db = SessionLocal()

# Criar tenant
tenant = Tenant(
    nome="Loja Exemplo",
    cnpj="12.345.678/0001-90",
    email="loja@exemplo.com",
    telefone="(24) 1234-5678",
    ativo=True
)
db.add(tenant)
db.commit()
db.refresh(tenant)

# Criar usuário admin
user = User(
    tenant_id=tenant.id,
    nome="Administrador",
    email="admin@exemplo.com",
    password_hash=get_password_hash("senha123"),
    role="admin",
    ativo=True
)
db.add(user)
db.commit()

print(f"Tenant criado: {tenant.id}")
print(f"Usuário criado: {user.id}")
print(f"Email: {user.email}")
print(f"Senha: senha123")
```

Ou execute via Python:
```bash
cd backend
python -c "
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.user import User

db = SessionLocal()
tenant = Tenant(nome='Loja Exemplo', cnpj='12.345.678/0001-90', email='loja@exemplo.com', ativo=True)
db.add(tenant)
db.commit()
db.refresh(tenant)
user = User(tenant_id=tenant.id, nome='Admin', email='admin@exemplo.com', password_hash=get_password_hash('senha123'), role='admin', ativo=True)
db.add(user)
db.commit()
print(f'Tenant: {tenant.id}, User: {user.email}')
"
```

## 5. Iniciar Servidores

### Backend

```bash
cd backend
uvicorn app.main:app --reload
```

O backend estará disponível em: http://localhost:8000
Documentação: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm run dev
```

O frontend estará disponível em: http://localhost:5173

## 6. Primeiro Acesso

1. Acesse http://localhost:5173
2. Faça login com:
   - Email: admin@exemplo.com (ou o email que você criou)
   - Senha: senha123 (ou a senha que você definiu)

## 7. Próximos Passos

1. **Criar Produtos**: Acesse a página de Produtos e adicione produtos da loja
2. **Criar Clientes**: Acesse a página de Clientes e adicione clientes
3. **Criar Primeira Cotação**: Use o botão "Nova Cotação" no dashboard
4. **Testar Fluxo Completo**:
   - Criar cotação
   - Enviar cotação
   - Aprovar cotação
   - Converter em pedido

## Troubleshooting

### Erro de Conexão com Banco de Dados

- Verifique se o PostgreSQL está rodando
- Verifique se a DATABASE_URL está correta
- Verifique se o usuário tem permissões

### Erro de Migrações

- Certifique-se de que o banco está vazio ou que você está usando um banco de teste
- Verifique se todas as dependências estão instaladas

### Erro de CORS

- Verifique se CORS_ORIGINS no backend inclui a URL do frontend
- Por padrão: http://localhost:5173

### Erro de Autenticação

- Verifique se o SECRET_KEY está configurado
- Verifique se o token está sendo enviado no header Authorization

