# Usuário de Teste

## Criar Usuário de Teste

Execute o script dentro do container do backend:

```bash
docker-compose exec backend python scripts/create_test_user.py
```

Ou se estiver rodando localmente (fora do Docker):

```bash
cd backend
python scripts/create_test_user.py
```

## Credenciais Padrão

Após executar o script, você terá:

- **Email**: `admin@teste.com`
- **Senha**: `senha123`
- **Role**: `admin`
- **Tenant**: `Loja de Teste`

## Usar no Sistema

1. Acesse o frontend: http://localhost:5173
2. Faça login com as credenciais acima
3. O Tenant ID será automaticamente identificado pelo token JWT

## Nota

O script verifica se o tenant e usuário já existem antes de criar. Se já existirem, apenas mostra as informações existentes.

