# BaseCommerce Infrastructure CLI

CLI profissional em Python para gerenciar a infraestrutura do BaseCommerce.

## Instalação

### Opção 1: Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar CLI
pip install -e .
```

### Opção 2: pipx (Alternativa)

```bash
pipx install -e .
```

**Nota**: O CLI requer Python 3.11+.

### Script Helper

Após a instalação, você pode usar o script helper:

```bash
./basec.sh status
./basec.sh smoke
```

Isso ativa automaticamente o ambiente virtual e executa o comando.

## Uso Rápido

```bash
# Status de todos os droplets
basec status

# Smoke tests
basec smoke

# Logs
basec logs edge nginx --follow

# Deploy
basec deploy edge

# Tenants
basec tenants list
basec tenants create novotenant --nome "Nova Loja" --email contato@exemplo.com
```

## Documentação Completa

Veja [../docs/infra-cli.md](../docs/infra-cli.md) para documentação completa.

