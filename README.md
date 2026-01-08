# Construção SaaS - Gestão de Cotações e Pedidos

Vertical SaaS para lojas de materiais de construção (Brasil)

## 📋 Visão Geral

Sistema completo para gestão de cotações, conversão em pedidos e inteligência de negócio para lojas de materiais de construção. Arquitetura modular com engines horizontais reutilizáveis e vertical específico.

**Stack Tecnológica**:
- **Backend**: Python 3.11+ com FastAPI
- **Frontend**: React 18+ com TypeScript
- **Banco de Dados**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **Autenticação**: JWT
- **Multi-tenant**: Por tenant_id nas tabelas

---

## 🗺️ Mapa de Leitura

### Para Desenvolvedores

1. **Comece aqui**: [`docs/README.md`](docs/README.md) - Documentação completa do sistema
2. **Arquitetura**: [`docs/architecture-overview.md`](docs/architecture-overview.md) - Visão geral da arquitetura
3. **Modelo de Domínio**: [`backend/docs/domain-model.md`](backend/docs/domain-model.md) - Entidades e regras de negócio
4. **Histórico de Implementação**: [`backend/docs/CHANGELOG.md`](backend/docs/CHANGELOG.md) - Changelog completo

### Para Product Managers

1. **Visão do Produto**: [`docs/00-product-vision.md`](docs/00-product-vision.md)
2. **Módulos e Fases**: [`docs/04-modules-and-phases.md`](docs/04-modules-and-phases.md)
3. **Fluxos Principais**: [`docs/03-core-flows.md`](docs/03-core-flows.md)
4. **Métricas de Sucesso**: [`docs/07-success-metrics.md`](docs/07-success-metrics.md)

### Para Stakeholders

1. **Visão do Produto**: [`docs/00-product-vision.md`](docs/00-product-vision.md)
2. **Módulos e Fases**: [`docs/04-modules-and-phases.md`](docs/04-modules-and-phases.md)
3. **Não-Objetivos**: [`docs/05-non-goals.md`](docs/05-non-goals.md)
4. **Riscos**: [`docs/06-assumptions-and-risks.md`](docs/06-assumptions-and-risks.md)

---

## 🏗️ Estrutura do Projeto

```
construction/
├── backend/                    # API FastAPI
│   ├── app/                    # Código da aplicação
│   │   ├── api/                # Endpoints HTTP
│   │   ├── application/        # Serviços de aplicação
│   │   ├── core/               # Configurações e utilitários
│   │   ├── core_engines/       # Engines horizontais
│   │   ├── domain/             # Regras de domínio
│   │   ├── models/             # Models SQLAlchemy
│   │   ├── platform/           # Plataforma (eventos, handlers)
│   │   └── schemas/            # Schemas Pydantic
│   ├── alembic/                # Migrations
│   ├── docs/                   # Documentação técnica
│   ├── scripts/                # Scripts utilitários
│   ├── tests/                  # Testes
│   ├── .pre-commit-config.yaml # Pre-commit hooks
│   ├── pyproject.toml          # Configuração ruff/black
│   ├── requirements.txt        # Dependências produção
│   └── requirements-dev.txt    # Dependências desenvolvimento
│
├── frontend/                   # React App
│   ├── src/                    # Código fonte
│   │   ├── components/         # Componentes React
│   │   ├── pages/              # Páginas
│   │   ├── services/           # Serviços API
│   │   └── hooks/              # React hooks
│   ├── .prettierrc             # Configuração Prettier
│   └── package.json            # Dependências Node
│
├── docs/                       # Documentação do produto
│   ├── 00-product-vision.md
│   ├── 01-domain-model.md
│   ├── 02-user-roles.md
│   ├── 03-core-flows.md
│   ├── 04-modules-and-phases.md
│   ├── 05-non-goals.md
│   ├── 06-assumptions-and-risks.md
│   ├── 07-success-metrics.md
│   ├── architecture-overview.md
│   ├── core-*.md               # Documentação dos engines
│   └── README.md               # Índice da documentação
│
├── docker-compose.yml          # Orquestração Docker
└── README.md                   # Este arquivo
```

---

## 🚀 Desenvolvimento

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker e Docker Compose (opcional)

### Backend

#### Setup Inicial

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Executar Aplicação

```bash
cd backend
uvicorn app.main:app --reload
```

#### Executar Testes

```bash
cd backend
pytest tests/ -v
```

#### Code Quality

```bash
cd backend

# Formatação (Black)
black app/ tests/

# Linting (Ruff)
ruff check app/ tests/

# Pre-commit (instalar hooks)
pre-commit install
```

### Frontend

#### Setup Inicial

```bash
cd frontend
npm install
```

#### Executar Aplicação

```bash
cd frontend
npm run dev
```

#### Code Quality

```bash
cd frontend

# Formatação (Prettier)
npm run format

# Verificar formatação
npm run format:check

# Linting (ESLint)
npm run lint

# Corrigir problemas de lint
npm run lint:fix
```

### Docker (Produção)

```bash
docker-compose up -d
```

---

## 📚 Documentação

### Documentação do Produto

Toda a documentação do produto está em [`docs/`](docs/). Comece pelo [`docs/README.md`](docs/README.md) para entender a estrutura.

### Documentação Técnica

- **Modelo de Domínio**: [`backend/docs/domain-model.md`](backend/docs/domain-model.md)
- **Histórico de Implementação**: [`backend/docs/CHANGELOG.md`](backend/docs/CHANGELOG.md)
- **Arquitetura**: [`docs/architecture-overview.md`](docs/architecture-overview.md)

### Engines Horizontais

- **Stock Intelligence**: [`docs/core-stock-intelligence.md`](docs/core-stock-intelligence.md)
- **Sales Intelligence**: [`docs/core-sales-intelligence.md`](docs/core-sales-intelligence.md)
- **Pricing & Supplier Intelligence**: [`docs/core-pricing-supplier-intelligence.md`](docs/core-pricing-supplier-intelligence.md)
- **Delivery & Fulfillment**: [`docs/core-delivery-fulfillment.md`](docs/core-delivery-fulfillment.md)

---

## 🏛️ Arquitetura

### Princípios

1. **Multi-tenant**: Isolamento total de dados por tenant
2. **Clean Architecture**: Separação em camadas (Domain, Application, Infrastructure)
3. **Engines Horizontais**: Módulos reutilizáveis genéricos
4. **Vertical Específico**: Módulos específicos de materiais de construção
5. **Event-Driven**: Comunicação assíncrona via eventos (Outbox Pattern)

### Camadas

- **API Layer**: Endpoints FastAPI, autenticação, validação
- **Application Layer**: Serviços de aplicação, orquestração
- **Domain Layer**: Regras de negócio puras, validadores
- **Infrastructure Layer**: Models SQLAlchemy, persistência
- **Platform Layer**: Eventos, handlers, outbox pattern

---

## 🧪 Testes

### Backend

```bash
cd backend
pytest tests/ -v                    # Todos os testes
pytest tests/unit/ -v               # Testes unitários
pytest tests/integration/ -v        # Testes de integração
```

### Frontend

```bash
cd frontend
npm run lint                        # Verificar linting
npm run format:check                # Verificar formatação
```

---

## 🔧 Ferramentas de Desenvolvimento

### Backend

- **Ruff**: Linter rápido (substitui flake8, isort, etc.)
- **Black**: Formatação automática de código
- **Pre-commit**: Hooks Git para qualidade de código
- **Pytest**: Framework de testes

### Frontend

- **ESLint**: Linter JavaScript/TypeScript
- **Prettier**: Formatação automática de código
- **TypeScript**: Tipagem estática

---

## 📊 Status do Projeto

**Versão Atual**: Fase 2.4 (Plataforma Foundations)

### MVP 1 ✅
- Gestão de cotações
- Conversão cotação → pedido
- Multi-tenant
- Testes end-to-end

### MVP 2 ✅
- 4 Core Engines implementados
- Endpoints de API para engines
- Hardening pass (autorização, testes, logging)

### Fase 2.4 ✅
- Outbox Pattern
- Eventos assíncronos
- Handlers dos engines
- Desacoplamento real

---

## 🤝 Contribuindo

1. Leia a documentação em [`docs/README.md`](docs/README.md)
2. Siga os padrões de código (Black, Ruff, Prettier)
3. Execute os testes antes de commitar
4. Use pre-commit hooks para garantir qualidade

---

## 📝 Licença

Este é um projeto privado.

---

**Última atualização**: Janeiro 2026
