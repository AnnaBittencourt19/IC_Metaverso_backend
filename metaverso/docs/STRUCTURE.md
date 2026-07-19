# 📁 Estrutura do Projeto IC Metaverso - Documentação Completa

## 🎯 Visão Geral

Este documento descreve a estrutura organizada do projeto IC Metaverso RAG Backend, explicando cada pasta e arquivo, seu propósito e como se relacionam.

---

## 📊 Fluxograma de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IC_METAVERSO_BACKEND                              │
│                  (Root do Projeto)                                   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼─────────┐  ┌───▼────────┐  ┌───▼──────────────┐
        │   📁 /app       │  │  📁 /docs  │  │  📁 /config      │
        │   (Core Backend)│  │(Docs +Docs)│  │  (Configuration) │
        └───────┬─────────┘  └───────┬────┘  └───┬──────────────┘
                │                    │           │
        ┌───────────────┬──────────┐  │       ┌───────────────────┐
        │               │          │  │       │                   │
    ┌───▼──┐   ┌───────▼──┐  ┌────▼──┴──┐  ┌─▼──────┐      ┌──────▼──┐
    │main  │   │config    │  │rag.py    │  │.env    │      │render   │
    │.py   │   │.py       │  │ingest.py │  │.env.ex│      │.yaml    │
    └───┬──┘   └──────┬───┘  └────┬─────┘  └───────┘      └─────────┘
        │             │           │
        │ (imports)   │           │
        ▼             ▼           ▼
    ┌──────────────────────────────────────┐
    │  Groq API + ChromaDB + LangChain     │
    │  (Processamento RAG)                 │
    └──────────────────────────────────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ /chroma_db   │
                 │  (Vetores)   │
                 └──────────────┘
```

---

## 📂 Estrutura Completa de Pastas

```
metaverso/
│
├── 📁 app/                          # CORE DA APLICAÇÃO
│   ├── __init__.py                  # Pacote Python
│   ├── main.py                      # ⭐ FastAPI app (370 linhas)
│   ├── config.py                    # Configurações centralizadas
│   ├── rag.py                       # Lógica RAG (909 linhas)
│   └── ingest.py                    # Ingestão de documentos
│
├── 📁 docs/                         # DOCUMENTAÇÃO
│   ├── UNITY_INTEGRATION.md         # 🎮 Guia Unity com código C#
│   ├── IMPLEMENTATION_SUMMARY.md    # ✅ Sumário das implementações
│   ├── INGEST_DOCUMENTATION.md      # 📚 Como ingerir documentos
│   ├── SETUP_SUMMARY.md             # 🔧 Resumo de setup
│   └── README_DOCS.md               # 📖 Índice de docs
│
├── 📁 config/                       # CONFIGURAÇÃO E DEPLOYMENT
│   ├── render.yaml                  # Deploy no Render
│   ├── Dockerfile                   # Containerização
│   └── .env.example                 # Template de env vars
│
├── 📁 chroma_db_export/             # BANCO DE DADOS VETORIAL
│   ├── chroma.sqlite3               # Dados ChromaDB
│   └── [IDs dos documentos]/         # Índices dos vetores
│
├── 📁 Data/                         # DOCUMENTOS DE ENTRADA
│   └── [PDFs e arquivos para ingestão]
│
├── 📁 tests/                        # TESTES (RECOMENDADO)
│   ├── test_api_complete.py         # Suite de testes da API
│   ├── test_config.py               # Testes de config
│   └── test_api.py                  # Testes básicos
│
├── 🔧 CONFIGURAÇÃO (ROOT)
│   ├── .env                         # ⚠️ Variáveis secretas (NÃO committar)
│   ├── requirements.txt             # Dependências Python
│   └── .gitignore                   # Arquivos ignorados no Git
│
├── 📜 DOCUMENTAÇÃO (ROOT)
│   ├── README.md                    # 📖 Readme principal
│   └── [outros .md]                 # Documentação diversa
│
└── 🚀 DEPLOYMENT
    └── render.yaml                  # Configuração Render
```

---

## 📋 Explicação Detalhada de Cada Pasta

### 1️⃣ **📁 `/app` - Core da Aplicação**

**Responsabilidade:** Contém toda a lógica backend

#### Arquivos:

**`__init__.py`**
- Marca a pasta como pacote Python
- Vazio (pode ter imports para facilitar uso)
- **Tamanho:** ~0 linhas
- **Propósito:** Estrutura Python

**`main.py`** ⭐ PRINCIPAL
- **Tamanho:** 370 linhas
- **Propósito:** API FastAPI
- **Funcionalidades:**
  - Inicialização da app FastAPI
  - Configuração CORS (para Unity WebGL)
  - Autenticação via API Key
  - Logging estruturado
  - 3 Endpoints:
    - `GET /` - Root (health básico)
    - `GET /api/v1/health` - Health check detalhado
    - `POST /api/v1/ask` - Processa pergunta (autenticado)
  - Exception handlers customizados
  - Documentação OpenAPI automática
- **Imports:** `FastAPI`, `Pydantic`, `hierarchical_search_and_generate` do rag.py

**`config.py`**
- **Tamanho:** ~40 linhas
- **Propósito:** Centralizar todas as configurações
- **Carrega:** Variáveis de `.env`
- **Contém:**
  - Diretórios (PDF_DIR, CHROMA_PERSIST_DIR)
  - Modelos (EMBEDDING_MODEL_NAME, CROSS_ENCODER_MODEL)
  - Parâmetros RAG (MIN_CROSS_ENCODER_SCORE, etc)
  - API Keys (GROQ_API_KEY)
- **Importado por:** main.py, rag.py, ingest.py

**`rag.py`** 🧠 INTELIGÊNCIA
- **Tamanho:** 909 linhas
- **Propósito:** Toda a lógica RAG (Retrieval-Augmented Generation)
- **Funcionalidades:**
  1. **Limpeza de texto** - Remove caracteres inválidos
  2. **Extração de PDFs** - Lê e processa arquivos PDF
  3. **Embeddings** - Converte texto em vetores (HuggingFace)
  4. **ChromaDB** - Armazena e recupera vetores
  5. **Busca hierárquica** - Prioriza PDFs sobre modelos
  6. **Reranking** - Cross-encoder para melhorar relevância
  7. **Geração** - Usa Groq para gerar respostas
  8. **Inicialização** - Setup global do RAG
- **Função Principal:** `hierarchical_search_and_generate(question)` → dict

**`ingest.py`**
- **Tamanho:** ~200 linhas (estimado)
- **Propósito:** Ingerir e preparar documentos
- **CLI Commands:**
  - `python -m app.ingest ingest` - Ingere PDFs
  - `python -m app.ingest status` - Verifica status
  - `python -m app.ingest reset` - Limpa banco (com confirmação)
- **Processo:**
  1. Lê PDFs do diretório `Data/`
  2. Divide em chunks
  3. Gera embeddings
  4. Armazena no ChromaDB

---

### 2️⃣ **📁 `/docs` - Documentação**

**Responsabilidade:** Guias e manuais de uso

#### Arquivos:

**`UNITY_INTEGRATION.md`** 🎮
- **Tamanho:** ~300 linhas
- **Para quem:** Desenvolvedores Unity
- **Contém:**
  - Explicação dos endpoints
  - Exemplo de código C# pronto para usar
  - CORS e autenticação
  - Troubleshooting
  - Checklist de integração

**`IMPLEMENTATION_SUMMARY.md`** ✅
- **Tamanho:** ~200 linhas
- **Para quem:** Equipe técnica
- **Contém:**
  - Resumo de todas as 10 melhorias implementadas
  - Como testar
  - Endpoints de exemplo
  - Próximos passos

**`INGEST_DOCUMENTATION.md`** 📚
- **Para quem:** Quem vai adicionar novos documentos
- **Contém:**
  - Como preparar PDFs
  - Como rodar ingestão
  - Troubleshooting de ingestão

**`SETUP_SUMMARY.md`** 🔧
- **Para quem:** DevOps / Setup inicial
- **Contém:**
  - Passo a passo de instalação
  - Configuração de ambiente
  - Variáveis necessárias

**`README_DOCS.md`** 📖
- **Índice de toda documentação**
- **Links para todos os guias**

---

### 3️⃣ **📁 `/config` - Configuração e Deployment**

**Responsabilidade:** Infraestrutura e deployment

#### Arquivos:

**`render.yaml`**
- Deploy automático no Render
- Especifica:
  - Comando de build
  - Comando de start
  - Variáveis de ambiente
  - Recursos (CPU, RAM)

**`Dockerfile`**
- Containerização da aplicação
- Para usar em Docker/Render
- Define:
  - Imagem base Python
  - Instalação de dependências
  - Comando de inicialização

**`.env.example`**
- Template de variáveis
- Para documentar o que cada variável faz
- **NUNCA committar `.env` real**

---

### 4️⃣ **📁 `/chroma_db_export` - Banco de Dados Vetorial**

**Responsabilidade:** Persistência de vetores

#### Arquivos:

**`chroma.sqlite3`**
- Banco de dados SQLite do ChromaDB
- Contém:
  - Metadados dos documentos
  - Índices
- **Tamanho:** Varia conforme documentos ingeridos

**`[UUIDs]/`**
- Diretórios com IDs dos documentos
- Armazenam dados relacionados

**⚠️ Importante:**
- Não committar para Git (arquivo muito grande)
- Usar `/var/data/chroma` em produção (Render Disk)

---

### 5️⃣ **📁 `/Data` - Documentos de Entrada**

**Responsabilidade:** PDFs e arquivos para ingestão

#### O que vai aqui:
- PDFs com documentação 6G
- Arquivos de treinamento
- Qualquer documento para ingerar

#### Como usar:
```bash
# 1. Coloque PDFs em /Data
# 2. Execute:
python -m app.ingest ingest

# 3. ChromaDB será atualizado automaticamente
```

---

### 6️⃣ **📁 `/tests` - Testes**

**Responsabilidade:** Validar funcionamento

#### Arquivos:

**`test_api_complete.py`** ⭐
- Suite completa de testes
- Testa:
  - Health check
  - Autenticação
  - CORS
  - Endpoint POST /ask
  - Serialização JSON
- **Como rodar:**
  ```bash
  python test_api_complete.py
  ```

**`test_config.py`**
- Testa carregamento de configurações
- Valida variáveis de ambiente

**`test_api.py`**
- Testes básicos da API
- Exemplos simples

---

## 🔄 Fluxo de Dados

### 1. **Ingestão** (Uma única vez ou periodicamente)
```
PDFs em /Data/
      ↓
   ingest.py (processa)
      ↓
   Chunks + Embeddings
      ↓
   ChromaDB (/chroma_db_export)
```

### 2. **Requisição** (Cada pergunta)
```
Cliente Unity
      ↓
POST /api/v1/ask (com X-API-Key)
      ↓
main.py (valida API key)
      ↓
rag.py:hierarchical_search_and_generate()
      ↓
   1. Query embedding (HuggingFace)
   2. Busca no ChromaDB (vetores similares)
   3. Reranking (Cross-encoder)
   4. Prompt building
   5. Groq API (gera resposta)
      ↓
JSON Response
      ↓
Cliente recebe resposta + sources + confidence
```

---

## 📊 Dependências Entre Arquivos

```
main.py
  ├── imports config.py
  ├── imports rag.py
  │    ├── imports config.py
  │    ├── imports ChromaDB
  │    ├── imports LangChain
  │    └── imports Groq
  │
  ├── FastAPI Framework
  ├── Pydantic (validação)
  └── CORS Middleware

ingest.py
  ├── imports config.py
  ├── imports rag.py (setup_vectorstore)
  ├── imports PyMuPDF (leitura PDF)
  └── imports ChromaDB

test_api_complete.py
  ├── imports requests
  ├── imports json
  └── (testa HTTP endpoints)
```

---

## 🔐 Arquivos de Configuração

### `.env` ⚠️ SECRETO
```
GROQ_API_KEY=xyz...      # Não exposar!
API_KEY=metaverso-key    # Não exposar!
UNITY_ORIGIN=http://...  # Configurável
CHROMA_PERSIST_DIR=...
PDF_DIR=./Data
```

**Regra:** Nunca committar `.env` no Git!

### `.env.example` ✅ PÚBLICO
Template de como montar `.env` local

### `.gitignore`
O que não enviar para Git:
- `.env` (variáveis secretas)
- `chroma_db_export/` (muito grande)
- `__pycache__/` (compilado Python)
- `venv/` (ambiente virtual)

---

## 🚀 Como Usar o Projeto

### Setup Inicial
```bash
# 1. Clone
git clone https://github.com/AnnaBittencourt19/IC_Metaverso_backend

# 2. Entre na pasta
cd metaverso

# 3. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instale dependências
pip install -r requirements.txt

# 5. Configure .env
cp .env.example .env
# Edite .env com suas chaves (GROQ_API_KEY, etc)

# 6. Ingira documentos
python -m app.ingest ingest

# 7. Inicie servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 8. Teste (em outro terminal)
python test_api_complete.py
```

### Integrar com Unity
Veja `docs/UNITY_INTEGRATION.md`

---

## 📈 Escalabilidade Futura

### Sugestões de melhorias:
```
/cache/                 # Cache de respostas
/logs/                  # Logs persistentes
/models/                # Modelos locais (se não usar Groq)
/scripts/               # Scripts auxiliares (backup, etc)
/migrations/            # Migrações de banco (se usar)
/monitoring/            # Prometheus, Grafana, etc
```

---

## ✅ Checklist de Funcionamento

- [ ] `/app/main.py` - FastAPI rodando
- [ ] `/app/config.py` - Variáveis carregadas
- [ ] `/app/rag.py` - RAG inicializado
- [ ] `/chroma_db_export/` - Banco de dados criado
- [ ] `.env` - Configurado com chaves reais
- [ ] `test_api_complete.py` - Todos os testes passando
- [ ] Unity consegue chamar API com autenticação

---

## 📞 Suporte

### Problemas comuns:

**"GROQ_API_KEY não está definida"**
- Verifique `.env`
- Rode: `echo $GROQ_API_KEY`

**"ChromaDB não foi inicializado"**
- Execute: `python -m app.ingest ingest`

**"CORS error em WebGL"**
- Verifique `UNITY_ORIGIN` em `.env`

**"API key rejeitada"**
- Confirme header `X-API-Key` está sendo enviado
- Validate o valor em `.env` (`API_KEY`)

---

## 🎯 Estrutura Recomendada para Contribuições

Se você vai adicionar novos features:

1. **Novo endpoint** → Edite `app/main.py`
2. **Nova lógica RAG** → Edite `app/rag.py`
3. **Novo teste** → Crie em `tests/test_nome.py`
4. **Documentar** → Atualize em `docs/`
5. **Commit** → Explique mudanças claramente

---

**Projeto IC Metaverso © 2026 - Anna Bittencourt**
