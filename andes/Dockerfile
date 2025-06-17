# ── Builder Stage ────────────────────────────────────────────────────────────
FROM python:3.11.5-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Instala dependencias de sistema para Python y Node
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential libgdbm-dev libpq-dev gcc \
      curl ca-certificates gnupg && \
    rm -rf /var/lib/apt/lists/*

# 2) Instalar Node.js 18
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
      | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" \
      > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# 3) Copiar y construir dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# 4) Copiar fuente y dependencias Node
COPY . .

# 5) Instalar dependencias Node y generar assets
RUN npm ci --legacy-peer-deps && \
    npm run build

# 6) Instalar Python desde las ruedas
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels \
    -r requirements.txt --prefix=/install

# 7) Preparar directorios estáticos y migraciones
ENV PATH=/install/bin:$PATH \
    PYTHONPATH=/install/lib/python3.11/site-packages

# ── Runtime Stage ────────────────────────────────────────────────────────────
FROM python:3.11.5-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=andes.settings

WORKDIR /app

# 1) Instalar runtime deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) Copiar paquetes Python instalados
COPY --from=builder /install /install
ENV PATH=/install/bin:$PATH \
    PYTHONPATH=/install/lib/python3.11/site-packages

# 3) Copiar la fuente completa (incluye static/dist)
COPY --from=builder /app /app

# 4) Crear STATIC_ROOT
RUN mkdir -p /app/staticfiles

EXPOSE 8000

# 5) Comando runtime: migrar, collectstatic y levantar dev server
CMD ["sh", "-c", "python manage.py migrate --no-input && python manage.py collectstatic --no-input && exec python manage.py runserver 0.0.0.0:8000"]
