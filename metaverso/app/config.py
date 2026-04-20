import os
from dotenv import load_dotenv

load_dotenv()

# Diretórios
# Local: ./Data ou ./chroma_db_export
# Render: /var/data/ (disco persistente)
PDF_DIR = os.getenv("PDF_DIR", "./Data")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db_export")

# Modelos
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-large")
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
ENABLE_RERANKER = os.getenv("ENABLE_RERANKER", "false").lower() == "true"
EAGER_RAG_INIT = os.getenv("EAGER_RAG_INIT", "false").lower() == "true"

# Parâmetros de Busca e Ranking
MIN_CROSS_ENCODER_SCORE = 0.15
MIN_RELATIVE_SCORE = 0.20
MAX_CONTEXT_TOKENS = 2000  # Reduzido de 3500 para economizar memória
INITIAL_RETRIEVAL_K = 6    # Reduzido de 12 para economizar memória

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "gemma-2-9b-it")  # Modelo atualmente disponível

# Lazy Loading - modelos são carregados apenas quando necessário
LAZY_LOAD_MODELS = True

# Request timeouts
REQUEST_TIMEOUT_SECONDS = 30

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY não está definida nas variáveis de ambiente")
