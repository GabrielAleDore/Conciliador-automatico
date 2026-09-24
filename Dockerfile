# ─── Stage 1: Build do Frontend (Node.js 22) ───────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Backend Python (runtime final) ────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema necessárias para pdfplumber/reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do backend
COPY backend/ ./backend/

# Copia o build do frontend para dentro do container
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expõe a porta (Railway injeta $PORT automaticamente)
EXPOSE 8000

# Working dir do runtime = pasta backend (para que `app.main` seja encontrado)
WORKDIR /app/backend

# Inicia o servidor
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
