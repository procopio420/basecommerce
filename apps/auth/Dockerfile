FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy basecore package
COPY packages/basecore /app/packages/basecore

# Copy auth service code
COPY apps/auth/src /app/src

# Install basecore package
RUN pip install --no-cache-dir -e /app/packages/basecore

# Install additional dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic-settings \
    pydantic[email] \
    sqlalchemy \
    psycopg2-binary \
    jinja2 \
    python-multipart

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "auth_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
