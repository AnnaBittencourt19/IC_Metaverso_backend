import logging
import json
import os
import tempfile
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from app.rag import hierarchical_search_and_generate, initialize_rag, process_audio_and_answer

# ============================================================================
# Configuração de Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Inicialização da aplicação
# ============================================================================

app = FastAPI(
    title="IC Metaverso RAG API",
    description="Sistema de Retrieval-Augmented Generation para integração com aplicações Unity",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# ============================================================================
# CORS - Crítico para Unity WebGL
# ============================================================================

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    os.getenv("UNITY_ORIGIN", ""),  # Origem do cliente Unity em produção
]

# Remover strings vazias
allowed_origins = [origin for origin in allowed_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# ============================================================================
# Autenticação via API Key
# ============================================================================

API_KEY = os.getenv("API_KEY", "metaverso-secret-key-2026")

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Valida a chave de API fornecida no header"""
    if not x_api_key:
        logger.warning("Tentativa de acesso sem API key")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key não fornecida no header X-API-Key"
        )
    if x_api_key != API_KEY:
        logger.warning(f"Tentativa com API key inválida: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida"
        )
    return x_api_key

# ============================================================================
# Inicialização na Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("🚀 Iniciando aplicação...")
        initialize_rag()
        logger.info("✅ RAG inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {str(e)}")
        raise

# ============================================================================
# Custom JSON Encoder para serialização de documentos
# ============================================================================

class DocumentEncoder(json.JSONEncoder):
    """Encoder customizado para serializar DocumentsChroma"""
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if hasattr(obj, 'page_content'):
            return {
                'content': obj.page_content,
                'metadata': getattr(obj, 'metadata', {})
            }
        return super().default(obj)

# ============================================================================
# Modelos Pydantic
# ============================================================================

class QuestionInput(BaseModel):
    question: str = Field(..., description="A pergunta a ser respondida pelo RAG", min_length=1, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "O que é 6G?"
            }
        }


class AudioResponse(BaseModel):
    """Resposta para requisições de áudio, incluindo a transcrição"""
    response: str = Field(..., description="Resposta gerada pelo RAG")
    audio_transcribed: str = Field(..., description="Texto transcrito do áudio")
    sources: List[SourceInfo] = Field(default_factory=list, description="Documentos usados como fonte")
    docs_used: int = Field(..., description="Número total de documentos consultados")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Momento da requisição")
    confidence: Optional[str] = Field(None, description="Nível de confiança da resposta")
    is_audio: bool = Field(default=True, description="Indicador de que foi processado áudio")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SourceInfo(BaseModel):
    content: str = Field(..., description="Conteúdo do documento fonte")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados do documento")


class ResponseOutput(BaseModel):
    response: str = Field(..., description="Resposta gerada pelo RAG")
    sources: List[SourceInfo] = Field(default_factory=list, description="Documentos usados como fonte")
    docs_used: int = Field(..., description="Número total de documentos consultados")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Momento da requisição")
    confidence: Optional[str] = Field(None, description="Nível de confiança da resposta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Momento do erro")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    status: str = Field(..., description="Status do servidor")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    rag_initialized: bool = Field(..., description="Se o RAG foi inicializado com sucesso")


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Verifica se a API está no ar"""
    logger.info("GET / - Root endpoint acessado")
    return {
        "status": "ok",
        "message": "IC Metaverso RAG API - Pronta para integração com Unity",
        "version": "1.0.0"
    }


@app.get("/api/v1/health", response_model=HealthResponse)
async def health():
    """Verifica o status da saúde do servidor"""
    logger.debug("GET /api/v1/health - Health check")
    return HealthResponse(
        status="healthy",
        rag_initialized=True
    )


@app.post("/api/v1/ask", response_model=ResponseOutput)
async def ask(
    input_data: QuestionInput,
    x_api_key: str = Header(None)
) -> ResponseOutput:
    """
    Processa uma pergunta e retorna a resposta gerada pelo RAG
    
    **Parâmetros:**
    - `question`: A pergunta a ser respondida
    
    **Headers obrigatórios:**
    - `X-API-Key`: Chave de autenticação da API
    
    **Retorna:**
    - `response`: A resposta gerada
    - `sources`: Lista de documentos consultados
    - `docs_used`: Número de documentos usados
    - `confidence`: Nível de confiança (alta/média/baixa)
    - `timestamp`: Data e hora da resposta
    """
    try:
        # Verificar API key
        verify_api_key(x_api_key)
        
        logger.info(f"📝 Nova pergunta recebida: {input_data.question[:50]}...")
        
        # Chamar a função RAG
        result = hierarchical_search_and_generate(input_data.question)
        
        # Extrair informações
        docs = result.get('docs', [])
        docs_used = len(docs) if docs else 0
        
        # Formatar sources
        sources = []
        if docs:
            for doc in docs:
                try:
                    if hasattr(doc, 'page_content'):
                        sources.append(SourceInfo(
                            content=doc.page_content,
                            metadata=getattr(doc, 'metadata', {})
                        ))
                    else:
                        sources.append(SourceInfo(
                            content=str(doc),
                            metadata={}
                        ))
                except Exception as e:
                    logger.warning(f"Erro ao serializar documento: {str(e)}")
                    continue
        
        response_data = ResponseOutput(
            response=result.get('response', ''),
            sources=sources,
            docs_used=docs_used,
            confidence=result.get('confidence', None)
        )
        
        logger.info(f"✅ Resposta gerada com sucesso - {docs_used} documentos usados")
        return response_data
        
    except HTTPException as e:
        logger.warning(f"⚠️ Erro HTTP: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao processar pergunta: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a pergunta: {str(e)}"
        )


@app.post("/api/v1/ask-audio", response_model=AudioResponse)
async def ask_audio(
    audio_file: UploadFile = File(..., description="Arquivo de áudio (MP3, WAV, M4A, etc)"),
    x_api_key: str = Header(None)
) -> AudioResponse:
    """
    Processa um arquivo de áudio, transcreve com Groq Whisper e gera resposta
    
    **Formatos de áudio suportados:**
    - MP3, WAV, M4A, FLAC, OGG, etc
    
    **Headers obrigatórios:**
    - `X-API-Key`: Chave de autenticação da API
    
    **Fluxo:**
    1. Recebe arquivo de áudio
    2. Transcreve com Groq Whisper (português)
    3. Processa texto com RAG
    4. Retorna resposta + transcrição
    
    **Retorna:**
    - `response`: A resposta gerada
    - `audio_transcribed`: O texto transcrito do áudio
    - `sources`: Lista de documentos consultados
    - `docs_used`: Número de documentos usados
    - `confidence`: Nível de confiança (alta/média/baixa)
    - `timestamp`: Data e hora da resposta
    """
    try:
        # Verificar API key
        verify_api_key(x_api_key)
        
        logger.info(f"🎤 Novo arquivo de áudio recebido: {audio_file.filename}")
        
        # Validar tipo de arquivo
        allowed_audio_types = [
            "audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg",
            "audio/flac", "audio/webm", "audio/x-m4a"
        ]
        
        if audio_file.content_type not in allowed_audio_types:
            logger.warning(f"Tipo de arquivo não suportado: {audio_file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não suportado: {audio_file.content_type}. Use MP3, WAV, M4A, FLAC, OGG, etc"
            )
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as tmp_file:
            contents = await audio_file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name
        
        try:
            # Processar áudio
            result = process_audio_and_answer(tmp_file_path)
            
            # Extrair informações
            docs = result.get('docs', [])
            docs_used = len(docs) if docs else 0
            
            # Formatar sources
            sources = []
            if docs:
                for doc in docs:
                    try:
                        if hasattr(doc, 'page_content'):
                            sources.append(SourceInfo(
                                content=doc.page_content,
                                metadata=getattr(doc, 'metadata', {})
                            ))
                        else:
                            sources.append(SourceInfo(
                                content=str(doc),
                                metadata={}
                            ))
                    except Exception as e:
                        logger.warning(f"Erro ao serializar documento: {str(e)}")
                        continue
            
            response_data = AudioResponse(
                response=result.get('response', ''),
                audio_transcribed=result.get('audio_transcribed', ''),
                sources=sources,
                docs_used=docs_used,
                confidence=result.get('confidence', None),
                is_audio=True
            )
            
            logger.info(f"✅ Áudio processado com sucesso - {docs_used} documentos usados")
            return response_data
            
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(tmp_file_path)
                logger.debug(f"Arquivo temporário removido: {tmp_file_path}")
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo temporário: {str(e)}")
    
    except HTTPException as e:
        logger.warning(f"⚠️ Erro HTTP: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao processar áudio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar o áudio: {str(e)}"
        )


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler customizado para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções não tratadas"""
    logger.error(f"Exceção não tratada: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# Lifespan (alternativa moderna ao on_event)
# ============================================================================

@app.get("/api/v1/info")
async def info():
    """Retorna informações sobre a API"""
    return {
        "name": "IC Metaverso RAG API",
        "version": "1.0.0",
        "description": "Sistema RAG otimizado para integração com Unity",
        "endpoints": {
            "health": "/api/v1/health",
            "ask": "/api/v1/ask",
            "docs": "/api/v1/docs"
        }
    }


# Modelos Pydantic

class QuestionInput(BaseModel):
    question: str


class ResponseOutput(BaseModel):
    response: str
    sources: list
    docs_used: int


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Verifica se a API está no ar"""
    return {"status": "ok", "message": "API está operacional"}


@app.get("/health")
async def health():
    """Verifica o status da saúde do servidor"""
    return {"status": "healthy"}


@app.post("/ask")
async def ask(input_data: QuestionInput) -> ResponseOutput:
    """
    Processa uma pergunta e retorna a resposta gerada pelo RAG
    
    Args:
        input_data: Contém o campo 'question' com a pergunta
        
    Returns:
        ResponseOutput com response, sources e docs_used
    """
    result = hierarchical_search_and_generate(input_data.question)
    
    # Extrair os documentos usados
    docs = result.get('docs', [])
    docs_used = len(docs) if docs else 0
    
    # Formatar as sources a partir dos documentos
    sources = []
    if docs:
        for doc in docs:
            sources.append({
                "content": doc.page_content if hasattr(doc, 'page_content') else str(doc),
                "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
            })
    
    return ResponseOutput(
        response=result.get('response', ''),
        sources=sources,
        docs_used=docs_used
    )
