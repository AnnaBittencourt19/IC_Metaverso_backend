# Guia de Deployment - Render + ChromaDB Persistente

## ❌ Problema Atual
```
"error": "Erro ao inicializar sistema RAG: Nenhum texto extraído dos PDFs em /var/data/pdfs"
```

### Causa
1. O ChromaDB não existe em `/var/data/chroma`
2. Os PDFs não existem em `/var/data/pdfs`
3. O código tenta reconstruir a base de dados, mas falha

---

## ✅ Solução: Upload do ChromaDB Existente

### Passo 1: Backup Local
```bash
# Criar backup do ChromaDB local
python3 backup_chroma.py

# Isso cria: chroma_backup/chroma_YYYYMMDD_HHMMSS/
```

### Passo 2: No Render Dashboard
1. **Acessar**: https://dashboard.render.com
2. **Seu Serviço** → **Disks**
3. **Connect a Shell** ao disco persistente
4. Executar:
```bash
# Conectar ao shell do disco
# Deletar conteúdo antigo (se existir)
rm -rf /var/data/chroma/*

# Upload dos arquivos (via SFTP ou Git)
# Os arquivos devem estar em /var/data/chroma/
```

### Passo 3: Redeploy
```bash
# No Render Dashboard
Settings → Manual Deploy → Latest Commit
```

---

## 🔄 Fluxo Automático (Alternativa)

Se quiser que Render recrie a base de dados automaticamente:

### 1. Adicione os PDFs a Render
```bash
# No shell do disco
cd /var/data
mkdir -p pdfs
# Copiar PDFs para pdfs/
```

### 2. Execute ingestão inicial
```bash
cd /app
python3 -m app.ingest ingest
```

### 3. Redeploy a aplicação

---

## 🧪 Verificar Status

### Health Endpoint
```bash
curl https://seu-servico.onrender.com/api/v1/health \
  -H "X-API-Key: metaverso-secret-key-2026"

# Esperado:
{
  "status": "healthy",
  "rag_initialized": true
}
```

### Memory Endpoint
```bash
curl https://seu-servico.onrender.com/api/v1/memory \
  -H "X-API-Key: metaverso-secret-key-2026"
```

---

## 📋 Checklist

- [ ] ChromaDB backup criado localmente (`python3 backup_chroma.py`)
- [ ] Render disk criado e montado em `/var/data`
- [ ] ChromaDB uploaded para `/var/data/chroma/`
- [ ] Environment variables configuradas:
  - [ ] `GROQ_API_KEY`
  - [ ] `CHROMA_PERSIST_DIR=/var/data/chroma`
  - [ ] `PDF_DIR=/var/data/pdfs`
- [ ] Serviço redemplyado
- [ ] Health endpoint retorna 200 OK
- [ ] /ask endpoint retorna respostas

---

## 🚨 Troubleshooting

### "Nenhum texto extraído dos PDFs"
**Solução**: Não há PDFs em `/var/data/pdfs`. 
- Opção A: Upload os PDFs
- Opção B: Restaure ChromaDB backup

### "Coleção vazia"
**Solução**: ChromaDB existe mas sem documentos.
- Faça backup local
- Delete `/var/data/chroma/*`
- Upload backup novamente

### "Connection refused"
**Solução**: ChromaDB path incorreto.
- Verifique `CHROMA_PERSIST_DIR=/var/data/chroma`
- Confirme que disco está montado em `/var/data`

---

## 📁 Estrutura Esperada no Render

```
/var/data/
├── chroma/
│   ├── chroma.sqlite3
│   └── [UUID-collections]/
└── pdfs/  (opcional, apenas se quiser reconstruir)
    └── *.pdf
```

---

## ✅ Próximas Etapas

1. Executar `python3 backup_chroma.py` localmente
2. Preparar ChromaDB para upload
3. Conectar shell ao disco Render
4. Fazer upload dos arquivos
5. Redeploy do serviço
6. Testar endpoints

---

**Data**: 20 de abril de 2026
**Status**: Guia para resolver 503 Service Unavailable
