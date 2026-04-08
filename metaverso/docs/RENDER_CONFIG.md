# 🔧 Configuração no Render - Diretórios e Variáveis

## 📍 Caminhos no Render vs Local

### Local Development
```
PDF_DIR = ./Data                    # Documentos para ingesta
CHROMA_PERSIST_DIR = ./chroma_db_export  # Banco de vetores
```

### Render Production
```
PDF_DIR = /var/data/pdfs            # Disco persistente (Render Disk)
CHROMA_PERSIST_DIR = /var/data/chroma   # Disco persistente (Render Disk)
```

---

## 🎯 O que está configurado

### render.yaml
```yaml
disks:
  - name: chroma-data
    sizeGB: 5
    mountPath: /var/data/chroma
    
envVars:
  - key: CHROMA_PERSIST_DIR
    value: /var/data/chroma
```

**Significa:**
- ✅ Disco de 5GB montado em `/var/data/chroma`
- ✅ Variável `CHROMA_PERSIST_DIR` já configurada
- ✅ ChromaDB persiste entre redeploys

### app/config.py
```python
PDF_DIR = os.getenv("PDF_DIR", "/var/data/pdfs")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/var/data/chroma")
```

**Significa:**
- ✅ Procura variáveis de ambiente primeiro (Render as define)
- ✅ Se não existir, usa padrão `/var/data/`
- ✅ Funciona tanto local quanto Render

---

## ✅ Variáveis Obrigatórias no Render

### Dashboard Render → Seu Serviço → Environment

**Adicione:**

```
GROQ_API_KEY = sua_chave_aqui
API_KEY = metaverso-secret-key-2026
CHROMA_PERSIST_DIR = /var/data/chroma
PDF_DIR = /var/data/pdfs
```

**Configuradas automaticamente pelo render.yaml:**
- ✅ `CHROMA_PERSIST_DIR` (já está no yaml)

**Você precisa adicionar:**
- ❌ `GROQ_API_KEY` (sua chave)
- ❌ `API_KEY` (para autenticação)
- ❌ `PDF_DIR` (opcional, já tem default)

---

## 📁 Estrutura de Diretórios no Render

```
/var/data/
├── chroma/              (Render Disk - Persistent)
│   ├── chroma.sqlite3   (Banco de vetores)
│   └── [IDs]/
│
└── pdfs/                (Render Disk - Para ingestão)
    └── [seus PDFs]
```

---

## 🔄 Como Usar

### 1. Arquivos que você enviou (GitHub)
```
seu-repo/
├── app/
├── docs/
├── tests/
├── .env.example
├── requirements.txt
└── config/render.yaml
```

### 2. Render cria automaticamente
```
/var/data/chroma/       ← Disco persistente (5GB)
/var/data/pdfs/         ← Opcional (você cria)
```

### 3. Seu código usa
```python
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/var/data/chroma")
```

---

## 🎯 Checklist Render

- [ ] `GROQ_API_KEY` adicionada em Environment
- [ ] `API_KEY` adicionada em Environment
- [ ] `render.yaml` está correto no repositório
- [ ] Disco "chroma-data" montado (verificar Dashboard)
- [ ] Serviço em status "Live"

---

## ⚠️ Importante

### ChromaDB Persiste?
✅ **SIM** - O disco `/var/data/chroma` persiste entre redeploys

### PDFs Precisam ser Ingeridos?
✅ **SIM** - Você precisa:
1. Uploar PDFs para `/var/data/pdfs` (ou enviar via script)
2. Rodar `python -m app.ingest ingest` no Render
3. Dados vão para ChromaDB

### Como Ingerir PDFs no Render?

**Opção 1: SSH no Render**
```bash
# Render Dashboard → Seu Serviço → Shell
python -m app.ingest ingest
```

**Opção 2: Script Python**
```python
import requests

# Conectar ao Render e executar ingestão
response = requests.get("https://seu-servico.onrender.com/api/v1/health")
print(response.json())

# Se você tiver um endpoint de ingestão
# POST /api/v1/ingest com os PDFs
```

---

## 🔍 Verificar Configuração

### No Render Dashboard
```
Seu Serviço → Environment
Procure por:
- CHROMA_PERSIST_DIR = /var/data/chroma ✅
- GROQ_API_KEY = (deve estar preenchida) ✅
```

### Testar via API
```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "Teste"}' \
  https://seu-servico.onrender.com/api/v1/ask
```

Se retornar 200 OK, tudo está funcionando! ✅

---

## 📊 Tamanho do Disco

**Configurado:** 5GB
**Uso estimado:**
- ChromaDB com 100 PDFs: ~1GB
- Espaço livre: ~4GB

**Se precisar aumentar:**
```
Render Dashboard → Seu Serviço → Disks → chroma-data → Edit
```

---

## 🚀 Próximo Passo

1. ✅ Código está no Render
2. ✅ Variáveis configuradas
3. ⏳ **Agora:** Verifique Environment no Dashboard
4. ⏳ **Depois:** Ingira os PDFs
5. ⏳ **Finally:** Teste a API

---

**Status:** ✅ Configuração Pronta
