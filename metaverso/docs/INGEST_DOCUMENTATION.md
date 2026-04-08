# 📚 INGEST.PY - Documentação Detalhada

## 📋 O Que É

`ingest.py` é o módulo responsável por gerenciar a **ingestão e indexação de documentos PDF** no banco de dados ChromaDB. Ele orquestra todo o pipeline de:

1. **Carregamento** de PDFs do diretório
2. **Processamento** de texto e tabelas
3. **Chunking** semântico
4. **Indexação** em ChromaDB com embeddings

## 📦 Imports

```python
import os                    # Operações com sistema de arquivos
import logging             # Logs estruturados
import shutil              # Manipulação de diretórios

# Do rag.py (evita duplicação):
from app.rag import load_pdfs_improved    # Carrega e processa PDFs
from app.rag import chunk_documents       # Cria chunks semânticos
from app.rag import setup_vectorstore     # Configura ChromaDB

# Do config.py:
from app.config import PDF_DIR           # Diretório de PDFs
from app.config import CHROMA_PERSIST_DIR # Diretório de persistência
```

## 🗂️ Caminhos (Locais)

```python
PDF_DIR = "/Users/annabittencourt/projetos/IC_METAVERSO/metaverso/Data"
CHROMA_PERSIST_DIR = "/Users/annabittencourt/projetos/IC_METAVERSO/metaverso/chroma_db_export"
```

## 🔧 Funções Principais

### 1. `reset_database()`

**Propósito**: Remove completamente o banco de dados ChromaDB

```python
def reset_database():
    """Remove completamente o banco de dados ChromaDB existente."""
```

**Retorna**: `bool` - True se removido com sucesso

**Uso**:
```python
reset_database()  # Apaga tudo
```

**⚠️ Cuidado**: Dados são perdidos!

---

### 2. `check_database_status()`

**Propósito**: Verifica se o banco existe e quantos documentos contém

```python
def check_database_status():
    """Verifica o status do banco de dados ChromaDB."""
```

**Retorna**: `tuple(bool, int)` - (existe, quantidade_documentos)

**Uso**:
```python
exists, count = check_database_status()
if exists:
    print(f"Banco tem {count} documentos")
```

---

### 3. `ingest_pdfs(pdf_directory=None)`

**Propósito**: Pipeline completo de ingestão de PDFs

**Fluxo**:
```
1. Carrega PDFs com load_pdfs_improved()
   ├─ Abre cada PDF
   ├─ Extrai texto página por página
   ├─ Extrai tabelas usando estratégias
   └─ Limpa e processa conteúdo

2. Cria chunks com chunk_documents()
   ├─ Divide semanticamente
   ├─ Mantém contexto
   └─ Respeita tamanhos máximos

3. Indexa com setup_vectorstore()
   ├─ Calcula embeddings
   ├─ Armazena em ChromaDB
   └─ Cria índices

4. Retorna estatísticas
```

**Parâmetros**:
- `pdf_directory` (str, opcional): Caminho dos PDFs. Se não especificado, usa `PDF_DIR`

**Retorna**: `dict`
```python
{
    "success": bool,         # True se ingestão completou
    "documents": int,        # Número de documentos
    "chunks": int,          # Número de chunks criados
    "message": str,         # Mensagem de status
    "error": str           # Se houve erro
}
```

**Exemplo**:
```python
# Usar diretório padrão
result = ingest_pdfs()

# Ou especificar diretório
result = ingest_pdfs("/caminho/para/pdfs")

if result["success"]:
    print(f"✅ {result['documents']} documentos indexados")
    print(f"📊 {result['chunks']} chunks criados")
else:
    print(f"❌ Erro: {result['error']}")
```

---

### 4. `get_database_info()`

**Propósito**: Retorna informações detalhadas do banco de dados

**Retorna**: `dict`
```python
{
    "exists": bool,              # Banco existe?
    "path": str,                 # Caminho do banco
    "documents": int,            # Quantidade de docs
    "unique_sources": list,      # Arquivos únicos
    "total_pages": int,          # Páginas totais
    "total_tables": int,         # Tabelas encontradas
    "source_count": int,         # Número de fontes
    "error": str                 # Se houve erro
}
```

**Exemplo**:
```python
info = get_database_info()

if info["exists"]:
    print(f"📚 {info['documents']} documentos")
    print(f"📄 {info['total_pages']} páginas")
    print(f"📊 {info['total_tables']} tabelas")
    print(f"📁 Fontes: {', '.join(info['unique_sources'])}")
else:
    print("Banco não foi criado ainda")
```

---

## 🖥️ Interface de Linha de Comando (CLI)

O arquivo pode ser executado como script:

```bash
# Ingeri PDFs (usa caminho padrão)
python -m app.ingest ingest

# Ingeri de um diretório específico
python -m app.ingest ingest /caminho/para/pdfs

# Verificar status do banco
python -m app.ingest status

# Remover banco (com confirmação)
python -m app.ingest reset
```

## 📊 Fluxo de Ingestão Detalhado

```
┌─────────────────────────────────────┐
│    PDFs em /Data                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  load_pdfs_improved() [de rag.py]  │
│  ├─ Abre cada PDF com PyMuPDF      │
│  ├─ Extrai tabelas (3 estratégias) │
│  ├─ Limpa texto (clean_text_content)│
│  └─ Retorna list de docs          │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  chunk_documents() [de rag.py]     │
│  ├─ Identifica blocos semânticos   │
│  ├─ Split inteligente              │
│  └─ Cria chunks de ~800-1500 chars │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  setup_vectorstore() [de rag.py]   │
│  ├─ Calcula embeddings (E5)        │
│  ├─ Armazena em ChromaDB           │
│  └─ Cria índices                   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    ChromaDB em chroma_db_export     │
│    Pronto para buscas!             │
└─────────────────────────────────────┘
```

## 🔌 Integração com Outros Módulos

```
ingest.py
├─ Importa funções de rag.py
│  ├─ load_pdfs_improved() - Carregamento
│  ├─ chunk_documents() - Processamento
│  └─ setup_vectorstore() - Indexação
│
├─ Usa configurações de config.py
│  ├─ PDF_DIR - Onde estão os PDFs
│  └─ CHROMA_PERSIST_DIR - Onde indexar
│
└─ Usa logging para rastreamento
   └─ Todos os eventos são registrados
```

## 💾 Dados Armazenados

No ChromaDB (`chroma_db_export/`):

```
chroma_db_export/
├─ data.db                    # Dados indexados
├─ *.parquet                  # Metadados
└─ .chroma/                   # Índices internos
```

Cada documento contém:
```json
{
  "content": "Texto do chunk...",
  "metadata": {
    "source": "documento.pdf",
    "page": 1,
    "path": "/caminho/completo.pdf",
    "tables_count": 0,
    "extraction_strategy": "text",
    "block_type": "paragraph"
  }
}
```

## 🚀 Exemplo Completo de Uso

```python
from app.ingest import ingest_pdfs, get_database_info

# 1. Verificar status inicial
print("Status inicial:")
info = get_database_info()
print(f"  Documentos: {info.get('documents', 0)}")

# 2. Ingeri PDFs
print("\nIngerindo PDFs...")
result = ingest_pdfs()

if result["success"]:
    print(f"✅ Sucesso!")
    print(f"  Documentos extraídos: {result['documents']}")
    print(f"  Chunks criados: {result['chunks']}")
    
    # 3. Verificar status final
    print("\nStatus final:")
    info = get_database_info()
    print(f"  Documentos indexados: {info['documents']}")
    print(f"  Páginas processadas: {info['total_pages']}")
    print(f"  Tabelas extraídas: {info['total_tables']}")
    print(f"  Fontes: {len(info['unique_sources'])}")
else:
    print(f"❌ Erro: {result['error']}")
```

## ⚙️ Configurações Relacionadas

Em `config.py`:

```python
PDF_DIR = "/Users/annabittencourt/projetos/IC_METAVERSO/metaverso/Data"
CHROMA_PERSIST_DIR = "/Users/annabittencourt/projetos/IC_METAVERSO/metaverso/chroma_db_export"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
MAX_CONTEXT_TOKENS = 3500
INITIAL_RETRIEVAL_K = 12
```

## 🔍 Logs Típicos

```
INFO - Iniciando ingestão de PDFs de: /Users/annabittencourt/projetos/IC_METAVERSO/metaverso/Data
INFO - Processando documento.pdf...
INFO - Páginas extraídas: 50 | Tabelas detectadas: 3
INFO - Total de chunks criados: 180
INFO - Recriando banco de dados...
INFO - Banco de dados carregado com 180 documentos
INFO - Ingestão concluída com sucesso!
```

## ❓ Troubleshooting

| Problema | Solução |
|----------|---------|
| "Diretório não existe" | Verificar caminho em `PDF_DIR` |
| "Nenhum PDF encontrado" | Verificar se há `.pdf` em `/Data` |
| "Erro ao acessar banco" | Deletar `chroma_db_export/` e reintentar |
| "Chunks vazios" | Verificar qualidade dos PDFs |

## 📝 Relacionados

- **rag.py**: Funções de processamento (`load_pdfs_improved`, `chunk_documents`)
- **config.py**: Configurações centralizadas
- **main.py**: API que usa banco indexado
- **test_api.py**: Testar após ingestão

---

**Criado em**: 8 de abril de 2026  
**Última atualização**: Hoje  
**Status**: ✅ Pronto para uso com dados em `/Data`
