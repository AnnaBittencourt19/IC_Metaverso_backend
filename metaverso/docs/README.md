# Metaverso 6G - Sistema RAG com Groq

Sistema de Retrieval-Augmented Generation (RAG) especializado em 6G, utilizando LangChain, ChromaDB e Groq API.

## 🚀 Funcionalidades

- **RAG Hierárquico**: Prioriza documentos PDF sobre modelos
- **Busca Inteligente**: Expansão de queries com glossário 6G e embeddings
- **Reranking**: Cross-encoder para melhorar relevância de resultados
- **API FastAPI**: Endpoints simples para integração
- **Persistência**: ChromaDB com suporte a Render Disk

## 📋 Pré-requisitos

- Python 3.10+
- Groq API Key (obtenha em https://console.groq.com/keys)
- ChromaDB Disk (se usar Render)

## 🔧 Instalação Local

### 1. Clone ou prepare o projeto

```bash
cd projetos/IC_METAVERSO/metaverso
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env`:

```bash
cp .env.example .env
```

Edite `.env` e adicione:

```
GROQ_API_KEY=sua_chave_aqui
CHROMA_PERSIST_DIR=./chroma_db
PDF_DIR=./pdfs
```

## 📚 Ingestão de Documentos

### Preparar PDFs

1. Crie um diretório `pdfs` na raiz do projeto
2. Copie seus arquivos PDF para este diretório

### Executar Ingestão

```bash
# Ingere PDFs e cria o banco de dados
python -m app.ingest ingest

# Verifica o status do banco
python -m app.ingest status

# Remove o banco (com confirmação)
python -m app.ingest reset
```

## ▶️ Executar o Sistema

### Servidor de desenvolvimento

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Servidor de produção (Render)

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📡 Usando a API

### Health Check

```bash
curl http://localhost:8000/health
```

### Fazer uma Pergunta

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é 6G?"}'
```

### Resposta Esperada

```json
{
  "response": "6G é a próxima geração...",
  "confidence": "alta",
  "confidence_desc": "✅ Alta (Maioria é PDF)",
  "total_docs": 4,
  "pdf_docs": 3,
  "model_docs": 1,
  "pdf_percentage": 75.0
}
```

## 🏗️ Arquitetura do Projeto

```
metaverso/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── config.py        # Configurações
│   ├── rag.py          # Lógica RAG (busca + geração)
│   └── ingest.py       # Ingestão de PDFs
├── render.yaml         # Configuração Render
├── requirements.txt    # Dependências Python
├── .env.example        # Template de variáveis
└── README.md
```

## 🔄 Fluxo de Operação

1. **Ingestão**: PDFs são processados em chunks semânticos
2. **Indexação**: Chunks são indexados no ChromaDB usando embeddings
3. **Query**: Usuário faz pergunta
4. **Busca Hierárquica**:
   - Expansão de query (glossário + embeddings)
   - Busca inicial no vectorstore
   - Reranking com cross-encoder
   - Filtro de relevância
5. **Geração**: Groq gera resposta usando contexto
6. **Resposta**: Sistema retorna resposta + metadados

## 🌐 Deploy no Render

### Configuração do render.yaml

O arquivo `render.yaml` já vem configurado com:
- Serviço web Python
- Build automático via pip
- Startup com uvicorn
- Render Disk de 5GB em `/var/data/chroma`

### Variáveis de Ambiente no Render

1. No painel Render, vá para Environment
2. Adicione `GROQ_API_KEY` com sua chave real
3. `CHROMA_PERSIST_DIR` já está configurado

### Primeiro Deploy com PDFs

1. Faça upload dos PDFs para `/var/data/pdfs` no servidor
2. Ou execute a ingestão via script SSH:

```bash
# Via SSH no Render
python -m app.ingest ingest /var/data/pdfs
```

## 🔑 Glossário 6G

O sistema inclui um glossário completo com 500+ termos técnicos em 6G:
- Formas de onda (OFDM, GFDM, F-OFDM, FBMC, UFMC, OTFS)
- Modulação e Codificação
- MIMO e Processamento de Sinal
- Comunicações Ópticas
- Espectro e Regulação
- E muito mais!

A expansão automática de queries usa este glossário para melhorar as buscas.

## 📊 Modelos Utilizados

- **Embedding**: `intfloat/multilingual-e5-large` (1024 dim)
- **Reranking**: `BAAI/bge-reranker-v2-m3`
- **LLM**: Groq com `mixtral-8x7b-32768`

## ⚙️ Parâmetros Configuráveis

No `config.py`:

```python
MIN_CROSS_ENCODER_SCORE = 0.15      # Score mínimo do reranker
MIN_RELATIVE_SCORE = 0.20           # Score relativo mínimo
MAX_CONTEXT_TOKENS = 3500           # Máximo de tokens de contexto
INITIAL_RETRIEVAL_K = 12            # Documentos iniciais recuperados
```

## 🐛 Troubleshooting

### "GROQ_API_KEY não está definida"
- Verifique o arquivo `.env`
- Confirme a chave no console Groq
- No Render, verifique Environment vars

### "Banco de dados não existe"
- Execute: `python -m app.ingest ingest`
- Verifique que PDFs estão em `PDF_DIR`

### "Nenhum documento encontrado"
- Confirme que PDFs estão no diretório correto
- Verifique logs de ingestão para erros de parsing

### Erro de memória no Render Free
- Reduce `INITIAL_RETRIEVAL_K` em config.py
- Reduz `MAX_CONTEXT_TOKENS`
- Use instâncias maiores se necessário

## 📝 Logs

Logs são enviados para console/stdout:

```bash
# Ver logs de ingestão
python -m app.ingest ingest 2>&1 | grep "INFO\|ERROR"

# Ver logs do servidor
tail -f ~/.pm2/logs/app-error.log
```

## 🔐 Segurança

- Nunca commita `.env` com credenciais reais
- Use `.env.example` como template
- Groq API Key sempre na variável de ambiente (não no código)
- Em produção, use gerenciador de secrets

## 📚 Referências

- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Groq API Docs](https://console.groq.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Render Docs](https://render.com/docs)

## 📄 Licença

[Defina sua licença aqui]

## ✉️ Contato

Para dúvidas ou sugestões, entre em contato com a equipe do projeto.
