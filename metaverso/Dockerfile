# Dockerfile para Metaverso 6G RAG
# Baseado em Python 3.11 slim para reduzir tamanho

FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Tornar o build mais previsível dentro do container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Atualizar tooling do pip antes de resolver dependências mais pesadas
RUN python -m pip install --upgrade pip setuptools wheel

# Instalar Python packages
RUN python -m pip install -r requirements.txt

# Copiar aplicação e dados
COPY app/ ./app/
COPY chroma_db_export/ ./chroma_db_export/

# Variáveis de ambiente
ENV PORT=8000
ENV CHROMA_PERSIST_DIR=./chroma_db_export

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Expor porta
EXPOSE ${PORT}

# Comando de inicialização
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
