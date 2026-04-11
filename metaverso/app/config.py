import os
from dotenv import load_dotenv

load_dotenv()

# Diretórios
# Local: ./Data ou ./chroma_db_export
# Render: /var/data/ (disco persistente)
PDF_DIR = os.getenv("PDF_DIR", "/var/data/pdfs")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/var/data/chroma")

# Modelos
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-small")
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
ENABLE_RERANKER = os.getenv("ENABLE_RERANKER", "false").lower() == "true"
EAGER_RAG_INIT = os.getenv("EAGER_RAG_INIT", "false").lower() == "true"

# Parâmetros de Busca e Ranking
MIN_CROSS_ENCODER_SCORE = 0.15
MIN_RELATIVE_SCORE = 0.20
MAX_CONTEXT_TOKENS = 3500
INITIAL_RETRIEVAL_K = 12

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "mixtral-8x7b-32768"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY não está definida nas variáveis de ambiente")
