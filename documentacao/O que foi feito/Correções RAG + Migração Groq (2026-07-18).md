## 1. Bugs corrigidos no RAG 
- **Healthcheck sempre `rag_initialized: true`** — `/api/v1/health` retornava `true` fixo, mesmo com o RAG nunca inicializado. Combinado com deploy quebrado, o Render reportava o serviço saudável mesmo fora do ar. Corrigido: `rag.py` agora tem `is_rag_initialized()` (checa se `retriever is not None`), e o endpoint usa isso.
- **Indicador de confiança sempre "Baixa"** — com `ENABLE_RERANKER=false` (default), os documentos retornavam sem `source_type` no metadata, então toda resposta virava "Desconhecido" e a confiança nunca passava de "baixa", mesmo vindo 100% de PDF. Corrigido em `ReRankingRetriever.get_relevant_documents` (`rag.py`): marca `source_type`/`retrieval_score` mesmo sem cross-encoder.
- **Validação de áudio rejeitava gravações do navegador** — comparação exata contra `Content-Type`; navegadores mandam `audio/webm;codecs=opus` (com parâmetros), que nunca batia com a lista permitida. Corrigido: extrai o mime real (`split(";")[0]`) antes de validar.
- **Upload de áudio com mime type genérico** — `mime_type` real do áudio agora é extraído em `main.py` e repassado até `transcribe_audio()` em vez de um valor fixo.
## 2. Reranker trocado para multilíngue
`CROSS_ENCODER_MODEL` era `cross-encoder/ms-marco-MiniLM-L-6-v2` — treinado só em inglês (MS MARCO), rankeava mal texto em português. Trocado para **`BAAI/bge-reranker-v2-m3`** (multilíngue, PT+EN entre 100+ idiomas). Só faz efeito quando `ENABLE_RERANKER=true` (continua `false` por default). Modelo bem maior (~1.1GB vs ~90MB)
## 3. Migração Gemini → Groq
- **Texto**: `gemma-2-9b-it` (descontinuado pela Groq) → **`llama-3.3-70b-versatile`**
- **Áudio**: **`whisper-large-v3-turbo`** (Groq), 2000 requisições/dia grátis
- Removida dependência `google-genai`, voltou `groq`

Arquivos alterados:
- `metaverso/app/config.py` — `GROQ_API_KEY`/`GROQ_MODEL` no lugar de `GEMINI_API_KEY`/`GEMINI_MODEL`
- `metaverso/app/rag.py` — `ModelManager`, `generate_answer()`, `transcribe_audio()`
- `metaverso/app/main.py` — docstrings do endpoint de áudio
- `metaverso/requirements.txt`
- `render.yaml` (raiz) e `metaverso/config/render.yaml` — env var `GROQ_API_KEY`
- `metaverso/.env.render` e `metaverso/config/.env.example`
- `metaverso/tests/test_config.py` — checagem de env var e dependência
- `metaverso/scripts/setup.sh` — também corrigido `venv/` → `.venv/`, caminho do `.env.example` (`config/`), diretório de PDFs (`Data/`, não `pdfs/`)
## 4. Testado localmente — funcionou
No próprio Mac M3 / 8GB RAM: subiu o servidor, pergunta real sobre 6G em `/api/v1/ask`, resposta correta em português citando 4 fontes de PDF, `confidence: alta`. Sem reranker ligado, o único modelo pesado local é o de embeddings (`multilingual-e5-large`, ~1.2GB); geração de texto e transcrição de áudio rodam na nuvem via Groq, não pesam na RAM local.
## 5. Como testar localmente

```bash
cd ~/projetos/IC_METAVERSO/metaverso

# 1. Ativar o ambiente virtual (já existe, com tudo instalado)
source .venv/bin/activate

# Se precisar criar do zero:
# python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 2. Conferir o .env (precisa de GROQ_API_KEY válida)
cat .env

# 3. Subir o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Swagger UI**: http://localhost:8000/api/v1/docs — clique em "Try it out" no endpoint desejado
- **curl**:
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -d '{"question":"O que é 6G?"}'
```

⚠️ **Duas chaves diferentes, não confundir:**
- `X-API-Key` (header da requisição) → `metaverso-secret-key-2026` (valor de `API_KEY` no `.env`) — protege a própria API.
- `GROQ_API_KEY` (só no `.env`) → a chave `gsk_...` da Groq — nunca vai num header de requisição pro próprio servidor.
**Parar o servidor**: `Ctrl+C` no terminal onde ele está rodando, ou `kill <PID>` (`ps aux | grep "uvicorn app.main"` pra achar o PID).
**Nota**: mudança no `.env` não é pega pelo `--reload` (ele só reinicia em mudança de arquivo `.py`) — precisa parar e subir de novo.
## 6. O que ainda não foi feito
- Nada commitado ainda — tudo isso está só no working tree.
- `metaverso/requeriments.txt` (nome com erro de digitação) é uma cópia desatualizada de `requirements.txt` — arquivo morto, confunde.
- `API_KEY` tem valor default hardcoded no código (`metaverso-secret-key-2026`) — se esquecer de setar no Render, fica protegido por uma chave pública conhecida.
- Bug de mismatch de device (CPU/MPS) em `backend/app/app/ia.py` — não é o serviço em produção (`metaverso/`), não foi corrigido.
- `.git` do repo está grande (~350MB), boa parte por causa de `chroma_db_export/chroma.sqlite3` versionado (hoje redundante, já que o Docker build reconstrói do zero) e sobras do `backend/app/` antigo.
