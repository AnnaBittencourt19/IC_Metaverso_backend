# 🐛 DEBUG: Erro 500 - Guia de Troubleshooting

## Problema
```
POST /api/v1/ask → HTTP 500 Internal Server Error
```

## Causas Possíveis e Soluções

### 1. **ChromaDB não consegue ser inicializado**
```python
# Sintoma:
# Setup vectorstore fails
# Erro: "Coleção vazia" ou "Arquivo não encontrado"

# Verificar:
ls -la /var/data/pdfs/         # ou ./Data/
ls -la /var/data/chroma/       # ou ./chroma_db_export/

# Solução:
# A) Se PDFs não existem:
#    Precisa fazer ingestão primeiro (veja ingest.py)
# B) Se diretório vazio:
#    mkdir -p /var/data/pdfs /var/data/chroma
```

### 2. **ModelManager falha ao carregar modelos**
```python
# Sintoma:
# "Failed to load SentenceTransformer"
# "No module named 'sentence_transformers'"

# Verificar:
python -c "from sentence_transformers import SentenceTransformer; print('OK')"

# Solução:
pip install -r requirements.txt
pip install sentence-transformers transformers torch
```

### 3. **Retriever é None**
```python
# Sintoma:
# "Retriever não inicializado!"
# retriever.get_relevant_documents() fails

# Verificar:
# Logs devem mostrar "🚀 Inicializando RAG"

# Solução:
# Ver logs completos do servidor para entender erro de init
```

### 4. **Groq API key inválida**
```python
# Sintoma:
# "Erro ao gerar resposta: 401 Unauthorized"

# Verificar:
echo $GROQ_API_KEY

# Solução:
# 1. Render Dashboard → Settings → Environment Variables
# 2. Verificar GROQ_API_KEY está presente
# 3. Verificar valor não tem espaços extras
```

### 5. **Memoria insuficiente**
```python
# Sintoma:
# Timeout ou OutOfMemory durante lazy load
# "Process killed: Out of memory"

# Verificar:
curl https://seu-dominio/api/v1/memory

# Solução:
# Aumentar limite de memória no Render
# ou
# ENABLE_RERANKER=false para economizar ~200MB
```

## Teste Passo-a-Passo

### Local (Com todas as dependências instaladas)

```bash
# 1. Verificar sintaxe
python -m py_compile app/main.py app/rag.py

# 2. Verificar imports
python -c "
from app.config import *
from app.rag import initialize_rag
from app.main import app
print('✅ Todos os imports OK')
"

# 3. Iniciar servidor com verbose
export LOGLEVEL=DEBUG
python -m uvicorn app.main:app --reload --log-level debug

# 4. Em outro terminal, fazer requisição
curl -X POST http://localhost:8000/api/v1/ask \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "teste"}' \
  -v  # verbose para ver headers

# 5. Ver logs completos
# Procurar por:
# ✅ "RAG já inicializado" ou "🚀 Inicializando RAG"
# ✅ "📝 Nova pergunta recebida"
# ✅ "📊 Hierarquia:"
# ❌ "❌ Erro ao inicializar RAG"
```

## Erros Comuns Esperados

### ✅ Esperado: Primeiro load lento
```
🚀 Inicializando RAG com lazy loading...
📦 Carregando SentenceTransformer...  [pode levar 30-60s na primeira vez]
✅ RAG inicializado com sucesso
```

### ✅ Esperado: Warnings de warnings
```
⚠️ Warning: This cache version is larger than expected
[Normal de cache de modelos]
```

### ❌ NÃO Esperado: TypeError
```
TypeError: unsupported operand type(s)
Significa há bug no código
```

## Se Tudo Falhar

### 1. Check Render Logs
```
Render Dashboard → IC_Metaverso_backend-1 → Logs tab
Procurar por: ❌ Erro ao inicializar
```

### 2. SSH into Render (se ativado)
```bash
# Render → Settings → SSH → Enable
ssh -i /path/to/key render@your-app.onrender.com

# No servidor:
cat /var/log/application.log | tail -100
ps aux | grep uvicorn
free -h  # Ver memória
```

### 3. Rollback
```bash
git log --oneline | head -3
git revert <commit_hash>
git push origin main
```

## Status Codes Esperados

| Code | Significado |
|------|------------|
| **200** | ✅ Sucesso (esperado) |
| **400** | ❌ Requisição inválida (ex: API key faltando) |
| **403** | ❌ API key incorreta |
| **500** | ❌ Erro no servidor (BUG) |
| **503** | ❌ Serviço indisponível (RAG não inicializado) |
| **504** | ❌ Timeout (requisição muito lenta) |

## Checklist de Correção

- [ ] Verificar sintaxe: `python -m py_compile app/*.py`
- [ ] Verificar imports: Todos os módulos instalados?
- [ ] Verificar config: `LAZY_LOAD_MODELS=true` em `config.py`?
- [ ] Verificar data: Existe `/var/data/pdfs/` ou `./Data/`?
- [ ] Verificar API: Existe `GROQ_API_KEY` em env vars?
- [ ] Verificar logs: Procurar por "❌ Erro"
- [ ] Teste local: Funciona com `uvicorn`?
- [ ] Teste remoto: `/api/v1/health` retorna 200?
- [ ] Teste requisição: POST `/api/v1/ask` com pergunta simples?

---

**Última atualização:** 2026-04-20  
**Versão:** 1.1.1 (Debug Enhanced)
