# Guia de Deploy

## Desenvolvimento Local

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ (para desenvolvimento local do backend)
- Node.js 18+ (para desenvolvimento local do frontend)
- PostgreSQL 15+ (ou usar Docker)

### Opção 1: Docker Compose (Recomendado)

1. Clone o repositório:
```bash
git clone <repo>
cd construction
```

2. Configure as variáveis de ambiente:
```bash
cp backend/.env.example backend/.env
# Edite backend/.env com suas configurações
```

3. Suba os serviços:
```bash
docker-compose up -d
```

4. Execute as migrações do banco de dados:
```bash
docker-compose exec backend alembic upgrade head
```

5. Acesse:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Opção 2: Desenvolvimento Local (Sem Docker)

#### Backend

1. Crie um ambiente virtual:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
```

2. Instale dependências:
```bash
pip install -r requirements.txt
```

3. Configure o banco de dados:
- Crie um banco PostgreSQL
- Configure a URL em `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/construcao_db
```

4. Execute migrações:
```bash
alembic upgrade head
```

5. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Instale dependências:
```bash
cd frontend
npm install
```

2. Configure variáveis de ambiente:
```bash
# Crie .env
VITE_API_URL=http://localhost:8000
```

3. Inicie o servidor de desenvolvimento:
```bash
npm run dev
```

## Produção

### Backend

1. Configure variáveis de ambiente:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=<sua-chave-secreta-aleatoria>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://seu-dominio.com
```

2. Build da imagem:
```bash
cd backend
docker build -t construcao-backend .
```

3. Execute:
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=... \
  -e SECRET_KEY=... \
  construcao-backend
```

### Frontend

1. Build para produção:
```bash
cd frontend
npm run build
```

2. Configure um servidor web (Nginx) para servir os arquivos estáticos em `dist/`.

3. Configure proxy reverso para a API:
```nginx
location /api {
    proxy_pass http://localhost:8000;
}
```

## Migrações do Banco de Dados

1. Criar nova migração:
```bash
cd backend
alembic revision --autogenerate -m "descricao da migracao"
```

2. Aplicar migrações:
```bash
alembic upgrade head
```

3. Reverter migração:
```bash
alembic downgrade -1
```

## Primeiro Usuário

Para criar o primeiro tenant e usuário, você precisa:

1. Criar um tenant manualmente no banco de dados
2. Criar um usuário vinculado ao tenant
3. Fazer login com as credenciais

(Em produção, crie um script de setup inicial)

## Segurança

- **NUNCA** commite arquivos `.env` com credenciais reais
- Use senhas fortes para produção
- Configure HTTPS em produção
- Use variáveis de ambiente para secrets
- Configure CORS adequadamente
- Mantenha dependências atualizadas

