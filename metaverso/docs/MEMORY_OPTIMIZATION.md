# Otimização de Memória - Correção do Erro 502

## Problema
A aplicação excedia o limite de memória do Render, causando erro 502 Bad Gateway:
```
Web Service IC_Metaverso_backend-1 exceeded its memory limit
```

## Causas Identificadas

### 1. **Modelos carregados globalmente**
- ❌ `SentenceTransformer`, `CrossEncoder`, `Groq` eram instanciados na startup
- ✅ Implementado **Lazy Loading** com `ModelManager`

### 2. **PDFs não eram liberados da memória**
- ❌ `fitz.open()` sem proper cleanup
- ✅ Adicionado `doc.close()` e `gc.collect()` em `load_pdfs_improved()`

### 3. **Parâmetros agressivos de busca**
- ❌ `INITIAL_RETRIEVAL_K = 12` (muitos documentos)
- ❌ `MAX_CONTEXT_TOKENS = 3500` (contexto muito grande)
- ✅ Reduzido para `INITIAL_RETRIEVAL_K = 6` e `MAX_CONTEXT_TOKENS = 2000`

### 4. **Sem proteção contra timeout**
- ❌ Requisições longas travavam a memória
- ✅ Decorador `@with_timeout()` com timeout de 30s

### 5. **Sem garbage collection após requisições**
- ❌ Memória acumulava entre requisições
- ✅ `gc.collect()` após cada `/ask` e `/ask-audio`

## Soluções Implementadas

### 1. **Lazy Loading com ModelManager** (`app/rag.py`)
```python
class ModelManager:
    """Carrega modelos apenas quando necessário"""
    
    @classmethod
    def get_embeddings(cls):
        # Carregado na primeira requisição
        
    @classmethod
    def get_cross_encoder(cls):
        # Carregado sob demanda (se ENABLE_RERANKER=true)
        
    @classmethod
    def get_groq_client(cls):
        # Instância reutilizada
```

**Economia:** ~400-500 MB se reranker desabilitado

### 2. **Gerenciamento de Recursos** (`app/rag.py`)
- ✅ Proper cleanup de PDFs: `doc.close()` + `del doc` + `gc.collect()`
- ✅ Cleanup após criação de vectorstore
- ✅ Limpeza automática no exit com `atexit.register()`

### 3. **Otimização de Parâmetros** (`app/config.py`)
```python
INITIAL_RETRIEVAL_K = 6          # ↓ de 12
MAX_CONTEXT_TOKENS = 2000        # ↓ de 3500
REQUEST_TIMEOUT_SECONDS = 30     # ← novo
```

**Economia:** ~20-30% menos memória por requisição

### 4. **Proteção contra Timeout** (`app/main.py`)
```python
@app.post("/api/v1/ask")
@with_timeout(seconds=REQUEST_TIMEOUT_SECONDS)
async def ask(...):
    # Interrompida após 30s
```

**Benefício:** Evita requisições travadas consumindo memória

### 5. **Monitoramento de Memória** (`app/main.py`)
```python
GET /api/v1/memory
```
Retorna:
- Uso de memória em MB
- Percentual de memória utilizada
- Estatísticas de garbage collection

## Checklist de Deploy

### Antes de fazer deploy:
- [ ] Instalar novo `psutil` em requirements.txt
- [ ] Revisar `config.py` - valores reduzidos
- [ ] Confirmar `LAZY_LOAD_MODELS = true`
- [ ] Testar endpoint `/api/v1/memory`

### Comandos para testar localmente:
```bash
# 1. Verificar memória
curl -H "X-API-Key: metaverso-secret-key-2026" \
  http://localhost:8000/api/v1/memory

# 2. Fazer uma pergunta (deve terminar rápido)
curl -X POST http://localhost:8000/api/v1/ask \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é 6G?"}'

# 3. Monitorar crescimento de memória em múltiplas requisições
for i in {1..5}; do
  curl ... (comando anterior)
  sleep 2
  curl ... /api/v1/memory
done
```

## Impacto Esperado

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|---------|
| Memória inicial | ~800 MB | ~300 MB | -63% |
| Por requisição | ~200 MB | ~80-100 MB | -50% |
| Pico máximo | ~1.2 GB | ~600 MB | -50% |
| Timeout crashes | Sim | Não | ✅ |

## Próximos Passos (Opcional)

1. **Batch processing**: Implementar fila de requisições
2. **Model unloading**: Descarregar modelos após X minutos de inatividade
3. **Request caching**: Cache de respostas comuns
4. **Compression**: Comprimir documentos no ChromaDB

## Referências
- [PyMuPDF (fitz) Memory Management](https://pymupdf.readthedocs.io/en/latest/)
- [LangChain Memory Management](https://python.langchain.com/)
- [Python Garbage Collection](https://docs.python.org/3/library/gc.html)
