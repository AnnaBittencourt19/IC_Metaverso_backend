# 🚀 Como Testar no Render

## 📋 Pré-requisitos

1. Código enviado para GitHub (`main` branch)
2. Render conectado ao repositório
3. Serviço já deployado no Render

---

## ✅ Passo 1: Verificar Deploy no Render

### 1.1 Acessar dashboard Render
```
https://dashboard.render.com
```

### 1.2 Localizar seu serviço
- Nome: Procure pelo nome do seu projeto (ex: `IC_Metaverso_backend`)
- Status: Deve estar em "Live" (verde)

### 1.3 Obter URL da API
```
https://seu-servico-random.onrender.com
```

**Exemplo real:**
```
https://ic-metaverso-rag-api.onrender.com
```

---

## 🧪 Passo 2: Testar Endpoints Básicos

### 2.1 Health Check (sem autenticação)
```bash
curl https://seu-servico.onrender.com/api/v1/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "rag_initialized": true,
  "timestamp": "2026-04-08T14:30:00"
}
```

### 2.2 Informações da API
```bash
curl https://seu-servico.onrender.com/api/v1/info
```

---

## 📝 Passo 3: Testar Endpoint POST (com autenticação)

### 3.1 Teste Simples com cURL

```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é 6G?"}' \
  https://seu-servico.onrender.com/api/v1/ask
```

**Resposta esperada (200 OK):**
```json
{
  "response": "6G é a próxima geração...",
  "sources": [...],
  "docs_used": 2,
  "confidence": "alta",
  "timestamp": "2026-04-08T14:30:05"
}
```

### 3.2 Se falhar com 403 (Forbidden)
**Problema:** API key incorreta
**Solução:** Verifique `.env` no Render
```
Settings → Environment Variables → API_KEY
```

### 3.3 Se falhar com 500 (Server Error)
**Verificar logs:**
1. Vá para "Logs" no dashboard Render
2. Procure por "❌" ou "ERROR"
3. Verifique se GROQ_API_KEY está correto

---

## 🎤 Passo 4: Testar Endpoint de Áudio

### 4.1 Preparar arquivo de áudio

Opção A: Usar arquivo local
```bash
# Se tiver um arquivo .mp3
ls -lh audio.mp3
```

Opção B: Criar arquivo de teste (Python)
```python
import pyttsx3

engine = pyttsx3.init()
engine.save_to_file("O que é 6G", "test.mp3")
engine.runAndWait()
```

### 4.2 Enviar para Render

```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -F "audio_file=@test.mp3" \
  https://seu-servico.onrender.com/api/v1/ask-audio
```

**Resposta esperada:**
```json
{
  "response": "6G é...",
  "audio_transcribed": "O que é 6G?",
  "sources": [...],
  "docs_used": 2,
  "confidence": "alta",
  "is_audio": true
}
```

---

## 🐍 Passo 5: Teste Automático (Python)

### 5.1 Script de teste

```python
import requests
import json

# Configuração
RENDER_URL = "https://seu-servico.onrender.com"
API_KEY = "metaverso-secret-key-2026"

# 1. Health check
print("1️⃣ Health Check...")
response = requests.get(f"{RENDER_URL}/api/v1/health")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# 2. Ask (texto)
print("\n2️⃣ Pergunta em Texto...")
response = requests.post(
    f"{RENDER_URL}/api/v1/ask",
    headers={"X-API-Key": API_KEY},
    json={"question": "O que é 6G?"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Resposta: {data['response'][:100]}...")
    print(f"   Docs: {data['docs_used']}")
    print(f"   Confiança: {data['confidence']}")
else:
    print(f"❌ Erro: {response.text}")

# 3. Ask (áudio)
print("\n3️⃣ Pergunta em Áudio...")
with open("test.mp3", "rb") as f:
    response = requests.post(
        f"{RENDER_URL}/api/v1/ask-audio",
        headers={"X-API-Key": API_KEY},
        files={"audio_file": f}
    )
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Transcrito: {data['audio_transcribed']}")
    print(f"   Resposta: {data['response'][:100]}...")
else:
    print(f"❌ Erro: {response.text}")

print("\n✅ Testes completos!")
```

### 5.2 Rodar script

```bash
python test_render.py
```

---

## 📊 Passo 6: Monitorar Performance

### 6.1 Verificar latência

```bash
# Medir tempo de resposta
time curl https://seu-servico.onrender.com/api/v1/health

# Ou com mais detalhes
curl -w "\nTempo total: %{time_total}s\n" \
  https://seu-servico.onrender.com/api/v1/health
```

**Esperado:**
- Health check: < 500ms
- Ask (texto): 5-15s
- Ask (áudio): 10-20s

### 6.2 Verificar logs no Render

```
Render Dashboard → Seu Serviço → Logs
```

Procure por:
- ✅ "✅ Resposta gerada com sucesso"
- ❌ "❌ Erro ao processar"
- ⚠️ "GROQ_API_KEY não está definida"

---

## 🔍 Troubleshooting

### Problema: 404 Not Found
```
GET https://seu-servico.onrender.com/api/v1/ask
```

**Solução:** Endpoint não existe
- Verifique se `main.py` foi atualizado
- Faça novo push para GitHub
- Render fará redeploy automático

### Problema: 500 Internal Server Error

**Verificar:**
1. Logs do Render (procure por "ERROR")
2. ChromaDB foi inicializado? (log "✅ RAG inicializado")
3. GROQ_API_KEY é válida?

```bash
# Verificar via logs
# Se vir: "❌ Erro na inicialização: ..."
# Significa que RAG não iniciou
```

### Problema: Timeout (>30s)

**Causa:** Render free tier é lento
**Solução:**
- Upgrade para plano pago (se necessário)
- Ou aceite latência maior

### Problema: "API key não fornecida"

**Verificar:**
1. Você está enviando o header?
   ```bash
   -H "X-API-Key: metaverso-secret-key-2026"
   ```

2. Verifique em Render:
   ```
   Settings → Environment → API_KEY
   ```

---

## 🎯 Checklist de Teste Completo

- [ ] Health check retorna 200 ✅
- [ ] GET /api/v1/info funciona ✅
- [ ] POST /api/v1/ask responde com 200 ✅
- [ ] Resposta contém todos os campos ✅
- [ ] POST /api/v1/ask-audio funciona (se tiver áudio) ✅
- [ ] Confiança é calculada corretamente ✅
- [ ] Documents retornam metadados ✅
- [ ] Latência é aceitável (< 20s) ✅

---

## 📈 Teste de Carga (Opcional)

Se quiser testar múltiplas requisições:

```bash
# 10 requisições simultâneas
for i in {1..10}; do
  curl -X POST \
    -H "X-API-Key: metaverso-secret-key-2026" \
    -H "Content-Type: application/json" \
    -d '{"question": "O que é 6G?"}' \
    https://seu-servico.onrender.com/api/v1/ask &
done

wait
echo "✅ Teste de carga completo"
```

---

## 🔗 Links Úteis

- **Dashboard Render:** https://dashboard.render.com
- **Logs em tempo real:** Dashboard → Seu Serviço → Logs
- **Variáveis de ambiente:** Dashboard → Seu Serviço → Environment
- **Documentação API:** https://seu-servico.onrender.com/api/v1/docs
- **ReDoc:** https://seu-servico.onrender.com/api/v1/redoc

---

## 💡 Dica Pro

### Auto-redeploy ao fazer push

O Render já faz automaticamente! Quando você faz:
```bash
git push origin main
```

O Render detecta e faz redeploy em ~2-5 minutos.

**Para acompanhar:**
```
Dashboard → Seu Serviço → Deployments
```

Procure pelo status "Building" ou "Deploy in progress"

---

## ✅ Quando Tudo Está Funcionando

Você deve ver:

**Terminal:**
```
✅ Health Check: 200 OK
✅ Ask (texto): 200 OK
✅ Ask (áudio): 200 OK - audio_transcribed: "..."
✅ Todos os testes passaram
```

**Render Logs:**
```
2026-04-08 14:30:05 ✅ RAG inicializado com sucesso
2026-04-08 14:30:10 📝 Nova pergunta recebida: O que é 6G?
2026-04-08 14:30:15 ✅ Resposta gerada com sucesso - 2 documentos usados
```

---

**Agora sua API está live! 🎉**
