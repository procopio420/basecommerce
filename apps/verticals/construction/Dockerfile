FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia pacotes compartilhados e instala
COPY packages/basecore /app/packages/basecore
COPY packages/engines_core /app/packages/engines_core
RUN pip install --no-cache-dir -e /app/packages/basecore
RUN pip install --no-cache-dir -e /app/packages/engines_core

# Copia código da vertical
COPY apps/verticals/construction/src /app/src
COPY apps/verticals/construction/alembic /app/alembic
COPY apps/verticals/construction/alembic.ini /app/alembic.ini

# Configura PYTHONPATH
ENV PYTHONPATH=/app/src

# Expõe porta
EXPOSE 8000

# Comando para rodar
CMD ["uvicorn", "construction_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
