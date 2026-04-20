# 📝 LISTA DE MODIFICAÇÕES

## 📋 ARQUIVOS MODIFICADOS

### 1. `app/config.py` (3 mudanças)
**Linhas alteradas:** 19-21, 26-32

**Mudanças:**
```python
# ANTES:
MAX_CONTEXT_TOKENS = 3500
INITIAL_RETRIEVAL_K = 12
# (sem novo timeout/lazy loading)

# DEPOIS:
MAX_CONTEXT_TOKENS = 2000      # ← reduzido
INITIAL_RETRIEVAL_K = 6         # ← reduzido
LAZY_LOAD_MODELS = True         # ← novo
REQUEST_TIMEOUT_SECONDS = 30    # ← novo
```

**Motivo:** Reduzir consumo de memória por requisição

---

### 2. `app/rag.py` (5 seções modificadas)

#### ✏️ Seção 1: Imports (Linhas 1-32)
**Adicionado:**
```python
import gc
import atexit
from contextlib import contextmanager
# + novos imports de config
```

#### ✏️ Seção 2: ModelManager (Linhas 36-84)
**Adicionado:** Classe inteira para lazy loading de modelos

#### ✏️ Seção 3: SentenceTransformerEmbeddings (Linhas 88-125)
**Modificado:** Lazy loading do modelo no @property

#### ✏️ Seção 4: load_pdfs_improved (Linhas 562-607)
**Modificado:** Adicionado cleanup de PDFs
```python
# ANTES:
doc.close()

# DEPOIS:
if doc:
    doc.close()
    del doc
    gc.collect()
```

#### ✏️ Seção 5: setup_vectorstore (Linhas 612-656)
**Modificado:** Cleanup após criação
```python
del documents
del chunks
gc.collect()
```

#### ✏️ Seção 6: ReRankingRetriever (Linhas 662-746)
**Modificado:** Usar lazy loading do cross encoder
```python
cross_encoder = self.cross_encoder or (
    ModelManager.get_cross_encoder() if ENABLE_RERANKER else None
)
```

#### ✏️ Seção 7: generate_answer (Linhas 830-897)
**Modificado:** Usar lazy loading do Groq client
```python
# ANTES:
groq_client = Groq(api_key=GROQ_API_KEY)

# DEPOIS:
groq_client = ModelManager.get_groq_client()
```

#### ✏️ Seção 8: transcribe_audio (Linhas 910-960)
**Modificado:** Usar lazy loading do Groq client
```python
# ANTES:
client = Groq()

# DEPOIS:
client = ModelManager.get_groq_client()
```

#### ✏️ Seção 9: initialize_rag (Linhas 1006-1022)
**Modificado:** Lazy loading de cross encoder
```python
# ANTES:
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL, device="cpu")

# DEPOIS:
# Será carregado sob demanda no retriever
cross_encoder = None
```

---

### 3. `app/main.py` (8 mudanças)

#### ✏️ Mudança 1: Imports (Linhas 1-16)
**Adicionado:**
```python
import signal
import gc
import psutil
from functools import wraps
# + import REQUEST_TIMEOUT_SECONDS
```

#### ✏️ Mudança 2: Proteção Timeout (Linhas 27-54)
**Adicionado:** Decorador `@with_timeout` completo

#### ✏️ Mudança 3: Startup Event (Linhas 94-115)
**Adicionado:** Memory logging
```python
try:
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(f"📊 Memória inicial: {mem_info.rss / 1024 / 1024:.1f} MB")
except:
    pass
```

#### ✏️ Mudança 4: Health + Memory Endpoint (Linhas 241-277)
**Adicionado:** Novo endpoint `/api/v1/memory`

#### ✏️ Mudança 5: Decorador @with_timeout no ask (Linha 281)
**Adicionado:**
```python
@app.post("/api/v1/ask", response_model=ResponseOutput)
@with_timeout(seconds=REQUEST_TIMEOUT_SECONDS)  # ← novo
async def ask(...):
```

#### ✏️ Mudança 6: GC em /ask (Linhas 336-341)
**Adicionado:**
```python
# Forçar garbage collection
gc.collect()
return response_data
```

#### ✏️ Mudança 7: Decorador @with_timeout no ask_audio (Linha 369)
**Adicionado:**
```python
@app.post("/api/v1/ask-audio", response_model=AudioResponse)
@with_timeout(seconds=REQUEST_TIMEOUT_SECONDS + 10)  # ← novo
async def ask_audio(...):
```

#### ✏️ Mudança 8: GC em /ask-audio (Linhas 460-465)
**Adicionado:**
```python
# Forçar garbage collection
gc.collect()
return response_data
```

---

### 4. `requirements.txt` (1 adição)
**Adicionado:**
```
psutil==5.9.6
```

---

## 📄 ARQUIVOS ADICIONADOS

### ✨ Novo: `MEMORY_OPTIMIZATION.md` (Documentação completa)
- Análise de problemas
- Soluções implementadas
- Impacto esperado
- Próximos passos

### ✨ Novo: `DEPLOY_GUIDE.md` (Guia de deployment)
- Steps detalhados de deploy
- Troubleshooting
- Métricas de sucesso
- Checklist final

### ✨ Novo: `QUICK_FIX.md` (Resumo executivo)
- Problema em 1 parágrafo
- 5 soluções principais
- Impacto em tabela
- Próximos passos rápidos

### ✨ Novo: `VISUAL_SUMMARY.md` (Análise visual)
- Diagrama antes/depois
- Comparativo de memória
- Timeline de execução
- Checklist de validação

### ✨ Novo: `test_memory_optimization.py` (Script de teste)
- Testa 5 requisições
- Monitora memória
- Gera relatório
- Valida otimizações

---

## 📊 ESTATÍSTICAS DE MUDANÇAS

```
Arquivos Modificados:    4
Arquivos Adicionados:    5
Linhas de Código:       +150 (imports, ModelManager, GC)
Imports Adicionados:    6
Funções Novas:          1 (ModelManager)
Decoradores Novos:      1 (@with_timeout)
Endpoints Novos:        1 (/api/v1/memory)
```

---

## 🔍 COMO REVISAR AS MUDANÇAS

### Git Diff (Local)
```bash
git diff HEAD^ app/config.py
git diff HEAD^ app/rag.py
git diff HEAD^ app/main.py
git diff HEAD^ requirements.txt
```

### Git Diff (GitHub)
```
https://github.com/seu-usuario/IC_METAVERSO/commit/NEW_COMMIT_HASH
```

### Arquivo por Arquivo
1. **config.py** - Apenas números mudaram
2. **rag.py** - Principais mudanças no cleanup
3. **main.py** - Timeout + monitoramento
4. **requirements.txt** - Adição de psutil

---

## ✅ VALIDAÇÃO PRÉ-DEPLOY

```bash
# 1. Sintaxe
python3 -m py_compile app/config.py app/main.py app/rag.py

# 2. Imports
python3 -c "from app.config import *; print('✅ Config')"
python3 -c "from app.main import app; print('✅ Main')"

# 3. Teste
python3 test_memory_optimization.py

# 4. Build Docker (se usar)
docker build . -t ic-metaverso:optimized
```

---

## 🚀 ROLLBACK (Se necessário)

```bash
# Reverter para versão anterior
git revert <commit_hash>
git push origin main

# Ou, se ainda não fez push:
git reset --hard HEAD^
```

---

**Versão:** 1.1.0 (Memory Optimized)  
**Data:** 2026-04-20  
**Status:** ✅ Ready for Review
