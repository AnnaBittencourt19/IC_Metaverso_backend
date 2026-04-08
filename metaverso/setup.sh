#!/bin/bash

# Script de setup rápido para desenvolvimento local
# Executa as etapas necessárias para colocar o sistema funcionando

set -e  # Exit on error

echo "=========================================="
echo "🚀 Setup Metaverso 6G RAG - Desenvolvimento"
echo "=========================================="
echo ""

# 1. Criar ambiente virtual
echo "1️⃣  Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Ambiente virtual criado"
else
    echo "   ✅ Ambiente virtual já existe"
fi

# 2. Ativar ambiente virtual
echo ""
echo "2️⃣  Ativando ambiente virtual..."
source venv/bin/activate || . venv/Scripts/activate
echo "   ✅ Ambiente ativado"

# 3. Instalar dependências
echo ""
echo "3️⃣  Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✅ Dependências instaladas"

# 4. Configurar .env
echo ""
echo "4️⃣  Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✅ Arquivo .env criado (edite com sua GROQ_API_KEY)"
    echo ""
    echo "   ⚠️  IMPORTANTE: Edite .env e adicione sua chave Groq:"
    echo "      nano .env"
else
    echo "   ✅ Arquivo .env já existe"
fi

# 5. Criar diretório de PDFs
echo ""
echo "5️⃣  Preparando diretórios..."
mkdir -p pdfs
mkdir -p chroma_db
echo "   ✅ Diretórios criados"

# 6. Testar configuração
echo ""
echo "6️⃣  Testando configuração..."
python test_config.py

# 7. Instruções finais
echo ""
echo "=========================================="
echo "✅ Setup Concluído!"
echo "=========================================="
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Edite o arquivo .env e adicione sua GROQ_API_KEY:"
echo "   nano .env"
echo ""
echo "2. Copie seus PDFs para o diretório 'pdfs/':"
echo "   cp ~/Downloads/*.pdf pdfs/"
echo ""
echo "3. Execute a ingestão de PDFs:"
echo "   python -m app.ingest ingest"
echo ""
echo "4. Inicie o servidor:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "5. Acesse a API em http://localhost:8000"
echo "   Swagger UI: http://localhost:8000/docs"
echo ""
echo "=========================================="
