# Revisão de código — IC_METAVERSO

Análise de `metaverso/`, `backend/` e das configs de deploy, em busca de erros de programação e de lógica. Organizado por severidade.

## Críticos (quebram o serviço em produção)

### 1. O Dockerfile usado no deploy real nunca copia os PDFs nem faz a ingestão

O `render.yaml` da raiz aponta `dockerfilePath: ./Dockerfile` (o Dockerfile da raiz, não o de `metaverso/`). Esse Dockerfile da raiz faz:

```dockerfile
COPY metaverso/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY metaverso/app/ ./app/
```

Ele nunca copia `metaverso/Data/` (os PDFs) para a imagem, e nunca roda `build_ingest.py`. Como o `render.yaml` da raiz também define um disco persistente vazio em `/var/data/chroma`, na primeira requisição o `setup_vectorstore()` não encontra a coleção, tenta reingerir a partir de `PDF_DIR` (`./Data`, relativo a `/app`) — e esse diretório simplesmente não existe na imagem. Resultado: `ValueError('Nenhum texto extraído dos PDFs...')` e a API de RAG quebrada em produção, mesmo com o container "saudável".

Esse Dockerfile da raiz está dessincronizado do `metaverso/Dockerfile` (que é mais completo: copia `Data/`, roda `build_ingest.py` no build). Ao que tudo indica, ficaram dois Dockerfiles divergentes e o deploy real usa o desatualizado.

**Correção sugerida:** apontar `dockerfilePath` do `render.yaml` da raiz para `metaverso/Dockerfile`, ou atualizar o Dockerfile da raiz para copiar `Data/` e rodar a ingestão.

### 2. `metaverso/Dockerfile` também está quebrado — `build_ingest.py` nunca é copiado para a imagem

Mesmo o Dockerfile mais completo (`metaverso/Dockerfile`) tem esse trecho:

```dockerfile
COPY app/ ./app/
COPY Data/ ./Data/
...
RUN python build_ingest.py
```

`build_ingest.py` vive em `metaverso/build_ingest.py` (raiz do projeto, fora de `app/`), mas nunca é copiado com `COPY build_ingest.py .`. Esse `RUN` vai falhar o build com `python: can't open file 'build_ingest.py': No such file or directory`.

**Correção:** adicionar `COPY build_ingest.py .` antes do `RUN python build_ingest.py`.

### 3. O indicador de "confiança" da resposta é sempre "Baixa" com a configuração padrão

Em `metaverso/app/config.py`, `ENABLE_RERANKER` tem default `false`. Em `ReRankingRetriever.get_relevant_documents` (`rag.py:739-743`), quando o reranker está desligado, os documentos são devolvidos **sem** que `doc.metadata['source_type']` seja definido — esse campo só é escrito dentro do bloco do cross-encoder (`rag.py:774`).

Depois, em `query_documents` (`rag.py:844-845`), qualquer documento sem `source_type == 'PDF'` cai em `model_docs`. Como o valor default do `.get()` é `'Desconhecido'`, **todo documento vira "Desconhecido"** por padrão — mesmo vindo 100% de PDF. Isso zera `pdf_percentage`, e `hierarchical_search_and_generate` sempre retorna `confidence = 'baixa'` (`❌ Baixa (Maioria é Modelo)`), e cada fonte aparece como `[Desconhecido | Score: 0.00]` — mesmo quando a resposta está perfeitamente embasada nos PDFs.

Ou seja: com a configuração padrão do repositório, o sistema rotula toda resposta como pouco confiável, independentemente da qualidade real. Isso provavelmente já confundiu o diagnóstico de outros bugs (os arquivos em `metaverso/docs/` mostram várias sessões de debug de erros 500/502, mas nenhuma menciona esse problema específico).

**Correção:** ou ligar `ENABLE_RERANKER=true` por padrão, ou preencher `source_type='PDF'` a partir do metadata mesmo quando o reranker está desabilitado (linha 743, antes do `return initial_docs[:self.top_k]`).

### 4. Mismatch de device (CPU vs MPS) em `backend/app/app/ia.py` — crash garantido em Mac com Apple Silicon

Linha 30 (nível de módulo):
```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

Dentro de `IASystem.initialize()` (linhas 733-744), existe uma variável **local** `device` que detecta corretamente `"cuda"`, `"mps"` ou `"cpu"` e é usada para carregar o modelo (`device_map: device`, linha 764). Mas essa variável é local ao método — não altera a `device` global do módulo.

A função `generate_answer()` (fora da classe) usa a variável global do módulo:
```python
inputs = {k: v.to(device) for k, v in inputs.items()}  # linha 630
```

Em um Mac com Apple Silicon (sem CUDA), a global `device` é sempre `torch.device("cpu")`, enquanto o modelo foi carregado em `"mps"` dentro de `initialize()`. Resultado: `RuntimeError` de tensores em devices diferentes na primeira pergunta feita ao sistema.

**Correção:** parametrizar `generate_answer(prompt, model, tokenizer, device, metadata=None)` e passar o `device` detectado em `initialize()`, ou guardar `self.device` na classe `IASystem` e usá-lo.

## Importantes

### 5. Upload de áudio para o Gemini provavelmente falha por causa da extensão do arquivo temporário

Em `metaverso/app/main.py`, `ask_audio` salva o upload em:
```python
tempfile.NamedTemporaryFile(delete=False, suffix=".audio")
```
E `transcribe_audio()` (em `rag.py`, recém-adaptado para Gemini) chama `client.files.upload(file=audio_file_path)` sem informar `mime_type` explicitamente. A biblioteca `google-genai` infere o tipo MIME pela extensão do arquivo — e `.audio` não é reconhecido, então o upload deve falhar ou ser tratado como tipo genérico (que o Gemini rejeita para áudio).

**Correção:** passar o `content_type` do upload original até `transcribe_audio` e usar `client.files.upload(file=path, config={"mime_type": content_type})`, ou nomear o arquivo temporário com a extensão real (ex.: extrair de `audio_file.filename`).

### 6. Validação de `content_type` do áudio é frágil

```python
allowed_audio_types = ["audio/mpeg", "audio/wav", "audio/mp4", ...]
if audio_file.content_type not in allowed_audio_types:
    raise HTTPException(400, ...)
```
Navegadores frequentemente mandam `Content-Type` com parâmetros, tipo `audio/webm;codecs=opus`. Como a comparação é `not in` (igualdade exata), esse tipo de gravação — muito comum vindo de `MediaRecorder` no navegador — é rejeitado mesmo sendo um formato suportado.

**Correção:** comparar só a parte antes do `;` (`audio_file.content_type.split(';')[0].strip()`).

### 7. `MAX_CONTEXT_TOKENS` conta caracteres, não tokens

Em `rag.py`, o "orçamento de contexto" (`MAX_CONTEXT_TOKENS = 2000`) é comparado com `len(content)` — contagem de caracteres, não de tokens. Nomear a constante como "tokens" é enganoso: na prática o contexto real passado ao LLM é bem menor do que o nome sugere (2000 caracteres ≈ 400-500 tokens), o que pode truncar prematuramente PDFs relevantes.

**Correção:** renomear para `MAX_CONTEXT_CHARS`, ou trocar a contagem por uma estimativa de tokens de verdade.

### 8. CORS inválido em `backend/app/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    ...
)
```
`allow_origins=["*"]` combinado com `allow_credentials=True` viola a especificação CORS — navegadores rejeitam a resposta quando o header `Access-Control-Allow-Origin` é `*` junto com `Access-Control-Allow-Credentials: true`. Só não deu problema ainda porque o cliente provavelmente não usa `credentials: 'include'`.

**Correção:** ou tirar `allow_credentials=True`, ou listar origins explícitas (como já é feito corretamente em `metaverso/app/main.py`).

## Menores / código morto

- **`backend/app/app/ia.py`, linhas 18-19**: defaults de `PDF_DIR`/`CHROMA_PERSIST_DIR` são caminhos absolutos da sua máquina (`/Users/annabittencourt/...`). Funciona só localmente; qualquer outra máquina/deploy sem as env vars setadas quebra.
- **Extração de tabelas morta em `metaverso/app/rag.py`**: `find_table_caption` e `extract_tables_markdown` existem mas nunca são chamadas — `load_pdfs_improved` usa só `_extract_text_pypdf`, e `_extract_table_text_fitz` é um stub que sempre retorna vazio (comentário confirma: "Legacy function - now disabled"). A lógica em `chunk_documents` que trata blocos tipo `'table'` nunca recebe esse tipo de bloco na prática.
- **Expansão de query por embeddings morta**: `ReRankingRetriever.get_relevant_documents` chama `expand_query(query)` sem passar `embeddings_model`/`vectorstore`, então `expand_query_with_embeddings` nunca roda — só a expansão via glossário funciona.
- **`backend/app/app/websocket.py`**: define um segundo `app = FastAPI()` sem nenhuma rota, não é importado por nada. Arquivo morto que pode confundir (ex.: alguém rodar `uvicorn app.websocket:app` por engano e não entender por que tudo dá 404).
- **`backend/app/app/mqtt.py`**: só tem comentários, nenhuma implementação — a integração MQTT com o ESP32/incubadora descrita na documentação ainda não existe no código.
- **`metaverso/app/main.py`, endpoint `/api/v1/health`**: sempre retorna `rag_initialized=True`, mesmo que o RAG nunca tenha sido inicializado com sucesso. Combinado com o Dockerfile quebrado (item 1), o healthcheck do Render vai reportar o serviço como saudável mesmo com a API de fato quebrada.
- **`API_KEY` default hardcoded** (`"metaverso-secret-key-2026"`) em `config.py` e nos `.env.render`/`render.yaml`: funciona como segredo mas está em texto puro no repositório; qualquer deploy que esqueça de sobrescrever a env var no Render fica com uma chave pública conhecida.
- **`backend/app/app/faiss_index.bin` / `faiss_metadata.json`**: arquivos de um índice FAISS que não é referenciado em nenhum lugar do `ia.py` atual (só usa Chroma) — sobras de uma versão anterior.

## Resumo

Os itens 1-4 são os que realmente colocam o serviço fora do ar ou geram respostas erradas silenciosamente; vale corrigir antes de mexer em qualquer outra coisa. O item 5 é novo (surgiu com a troca Groq→Gemini desta sessão) e merece atenção rápida antes de testar a transcrição de áudio.
