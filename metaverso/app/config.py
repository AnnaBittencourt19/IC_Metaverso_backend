import os
from dotenv import load_dotenv

load_dotenv()

# Diretórios
# Local: ./Data ou ./chroma_db_export
# Render: /var/data/ (disco persistente)
PDF_DIR = os.getenv("PDF_DIR", "./Data")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db_export")

# Modelos
# multilingual-e5-large (560M params, ~2.2GB em memória) estoura o limite de
# 512MB do free tier do Render tanto no build (ingestão) quanto no runtime
# (embedding de query) — troquei para o small (118M params, ~470MB) por isso.
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-small")
# bge-reranker-v2-m3: multilíngue (PT+EN), compatível com a mesma API
# CrossEncoder do sentence-transformers. O antigo ms-marco-MiniLM-L-6-v2 é
# treinado só em inglês, então rankeava mal texto em português quando o
# reranker estava ligado (ENABLE_RERANKER=true).
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "BAAI/bge-reranker-v2-m3")
ENABLE_RERANKER = os.getenv("ENABLE_RERANKER", "false").lower() == "true"
EAGER_RAG_INIT = os.getenv("EAGER_RAG_INIT", "false").lower() == "true"

# Parâmetros de Busca e Ranking
# Ambos os cross-encoders (ms-marco e bge-reranker-v2-m3) retornam logits
# crus na mesma ordem de grandeza (~-10 a 10), então os thresholds abaixo
# continuam válidos, mas vale reavaliar empiricamente ao trocar de modelo.
MIN_CROSS_ENCODER_SCORE = 0.15
MIN_RELATIVE_SCORE = 0.20
MAX_CONTEXT_CHARS = 2000  # Reduzido de 3500 para economizar memória (conta caracteres, não tokens)
INITIAL_RETRIEVAL_K = 6    # Reduzido de 12 para economizar memória

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# gemma-2-9b-it foi descontinuado pela Groq; llama-3.3-70b-versatile é o
# modelo de texto atual, gratuito no free tier e com bom suporte a PT/EN.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Lazy Loading - modelos são carregados apenas quando necessário
LAZY_LOAD_MODELS = True

# Request timeouts
REQUEST_TIMEOUT_SECONDS = 30

import logging as _logging
if not GROQ_API_KEY:
    _logging.warning("GROQ_API_KEY não está definida - endpoints RAG não funcionarão")
