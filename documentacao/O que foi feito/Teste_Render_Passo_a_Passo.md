# 🧪 TESTE NO RENDER - GUIA COMPLETO E PRÁTICO

## 📋 Índice
1. [Preparação Inicial](#preparação-inicial)
2. [Teste 1: Health Check](#teste-1-health-check)
3. [Teste 2: Info da API](#teste-2-info-da-api)
4. [Teste 3: Pergunta em Texto](#teste-3-pergunta-em-texto)
5. [Teste 4: Pergunta em Áudio](#teste-4-pergunta-em-áudio)
6. [Teste 5: Segurança (Autenticação)](#teste-5-segurança-autenticação)
7. [Teste 6: Erros e Validação](#teste-6-erros-e-validação)
8. [Script Automático](#script-automático-teste-tudo)
9. [Troubleshooting](#troubleshooting)
10. [Checklist Final](#checklist-final)

---

## 🔧 Preparação Inicial

### Passo 1: Conseguir a URL do Render

```
1. Acesse: https://dashboard.render.com
2. Clique em seu serviço (ic-metaverso-rag-api ou similar)
3. Copie a URL no topo da página

Exemplo: https://ic-metaverso-rag-api.onrender.com
```

### Passo 2: Ter a API Key

```bash
# Essa é a chave padrão (se não mudou)
metaverso-secret-key-2026

# OU

# Se mudou, procure em Render:
# Dashboard → Seu Serviço → Environment
# Procure por: API_KEY
```

### Passo 3: Ferramentas Necessárias

Escolha UMA opção:

**Opção A: cURL (terminal - RECOMENDADO)**
```bash
# macOS/Linux - já tem
# Windows - instale: https://curl.se/download.html
```

**Opção B: Postman (interface gráfica)**
```
Baixe em: https://www.postman.com/downloads/
```

**Opção C: Python (mais completo)**
```bash
pip install requests
```

---

## ✅ TESTE 1: Health Check

### 🎯 O que testa?
- ✅ Servidor está ligado?
- ✅ API responde?
- ✅ ChromaDB está pronto?

### 🌐 Opção 1: Navegador (Mais fácil!)

```
Abra no navegador:
https://seu-servico.onrender.com/api/v1/health
```

**Você deve ver:**
```json
{
  "status": "healthy",
  "rag_initialized": true,
  "timestamp": "2026-04-18T10:30:45Z"
}
```

### 📱 Opção 2: cURL

```bash
curl https://seu-servico.onrender.com/api/v1/health
```

**Resposta esperada:**
```
HTTP/1.1 200 OK
{
  "status": "healthy",
  "rag_initialized": true
}
```

### 🐍 Opção 3: Python

```python
import requests

url = "https://seu-servico.onrender.com/api/v1/health"
response = requests.get(url)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

---

## ✅ TESTE 2: Info da API

### 🎯 O que testa?
- ✅ Configurações estão corretas?
- ✅ Modelos foram carregados?
- ✅ Que versão está rodando?

### 📱 cURL

```bash
curl https://seu-servico.onrender.com/api/v1/info
```

**Resposta esperada:**
```json
{
  "name": "IC Metaverso RAG API",
  "version": "1.0.0",
  "description": "Sistema de Retrieval-Augmented Generation",
  "models": {
    "embedding": "intfloat/multilingual-e5-small",
    "llm": "Groq - mixtral-8x7b-32768",
    "reranker": "cross-encoder/ms-marco-MiniLM-L-6-v2"
  },
  "features": [
    "RAG com busca hierárquica",
    "Processamento de áudio",
    "Autenticação via API Key"
  ]
}
```

### 🐍 Python

```python
import requests

url = "https://seu-servico.onrender.com/api/v1/info"
response = requests.get(url)

info = response.json()
print(f"API: {info['name']}")
print(f"Versão: {info['version']}")
print(f"Modelos: {info['models']}")
```

---

## ✅ TESTE 3: Pergunta em Texto

### 🎯 O que testa?
- ✅ API recebe perguntas?
- ✅ RAG busca documentos?
- ✅ IA gera respostas?
- ✅ Resposta tem formato correto?

### 📱 cURL

```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é machine learning?"}' \
  https://seu-servico.onrender.com/api/v1/ask
```

**Resposta esperada:**
```json
{
  "answer": "Machine learning é um tipo de inteligência artificial que permite que computadores aprendam...",
  "sources": [
    "documento.pdf - página 5",
    "documento.pdf - página 12"
  ],
  "confidence": 0.87,
  "timestamp": "2026-04-18T10:35:20Z",
  "processing_time_ms": 2345.67
}
```

### 🌐 Postman

```
1. Novo Request
2. Método: POST
3. URL: https://seu-servico.onrender.com/api/v1/ask
4. Headers:
   X-API-Key: metaverso-secret-key-2026
   Content-Type: application/json
5. Body (raw, JSON):
   {
     "question": "O que é machine learning?"
   }
6. Send
```

### 🐍 Python

```python
import requests
import json

url = "https://seu-servico.onrender.com/api/v1/ask"
headers = {
    "X-API-Key": "metaverso-secret-key-2026",
    "Content-Type": "application/json"
}
data = {
    "question": "O que é machine learning?"
}

response = requests.post(url, headers=headers, json=data)

print(f"Status: {response.status_code}")
result = response.json()
print(f"\nPergunta: O que é machine learning?")
print(f"\nResposta: {result['answer']}")
print(f"\nSources: {result['sources']}")
print(f"Confiança: {result['confidence']:.0%}")
print(f"Tempo: {result['processing_time_ms']:.0f}ms")
```

### ⏱️ Tempo Esperado

```
Render Free Tier: 3-10 segundos (primeiro acesso pode ser lento)
Render Paid: 1-3 segundos
```

---

## ✅ TESTE 4: Pergunta em Áudio

### 🎯 O que testa?
- ✅ Upload de arquivo funciona?
- ✅ Transcrição de áudio funciona?
- ✅ Groq Whisper está configurado?

### Passo 1: Criar um Arquivo de Áudio

**Opção A: Usar arquivo existente**
```bash
# Se você já tem um arquivo .mp3, .wav, etc
ls *.mp3
```

**Opção B: Criar com Python (macOS/Linux)**
```python
# Instalar primeiro:
# pip install pyttsx3

import pyttsx3

engine = pyttsx3.init()
engine.save_to_file("O que é machine learning?", "test_audio.mp3")
engine.runAndWait()

print("✅ Arquivo criado: test_audio.mp3")
```

**Opção C: Criar com shell (macOS)**
```bash
# Usar VoiceOver do macOS
say "O que é machine learning?" -o test_audio.aiff
```

### Passo 2: Enviar Áudio para API

**📱 cURL**

```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -F "audio_file=@test_audio.mp3" \
  https://seu-servico.onrender.com/api/v1/ask-audio
```

**Resposta esperada:**
```json
{
  "audio_transcribed": "O que é machine learning?",
  "answer": "Machine learning é um tipo de inteligência artificial que permite que computadores aprendam...",
  "sources": [
    "documento.pdf - página 5"
  ],
  "confidence": 0.85,
  "timestamp": "2026-04-18T10:40:15Z",
  "processing_time_ms": 4567.89
}
```

**🌐 Postman**

```
1. Novo Request
2. Método: POST
3. URL: https://seu-servico.onrender.com/api/v1/ask-audio
4. Headers:
   X-API-Key: metaverso-secret-key-2026
5. Body:
   Form Data
   Key: audio_file
   Value: [selecione seu arquivo]
6. Send
```

**🐍 Python**

```python
import requests

url = "https://seu-servico.onrender.com/api/v1/ask-audio"
headers = {
    "X-API-Key": "metaverso-secret-key-2026"
}

# Abrir arquivo de áudio
with open("test_audio.mp3", "rb") as f:
    files = {"audio_file": f}
    response = requests.post(url, headers=headers, files=files)

print(f"Status: {response.status_code}")
result = response.json()

print(f"\nAúdio transcrito: {result['audio_transcribed']}")
print(f"\nResposta: {result['answer']}")
print(f"\nSources: {result['sources']}")
print(f"Confiança: {result['confidence']:.0%}")
print(f"Tempo: {result['processing_time_ms']:.0f}ms")
```

### ⏱️ Tempo Esperado

```
Transcrição (Groq Whisper): 2-3 segundos
Processamento RAG: 2-3 segundos
Total: 4-6 segundos
```

### 🎙️ Formato de Áudio Suportado

```
✅ MP3
✅ WAV
✅ M4A (iPhone)
✅ OGG
✅ FLAC
✅ WEBM

❌ Formatos NÃO suportados:
  - MIDI
  - AIFF (Possivelmente)
  - Vídeos (MP4, MKV, etc)
```

---

## ✅ TESTE 5: Segurança (Autenticação)

### 🎯 O que testa?
- ✅ API Key é obrigatória?
- ✅ Chave errada é rejeitada?
- ✅ API está protegida?

### Teste A: SEM API Key (deve falhar com 403)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é AI?"}' \
  https://seu-servico.onrender.com/api/v1/ask
```

**Resposta esperada:**
```
HTTP/1.1 403 Forbidden
{
  "detail": "API key não fornecida no header X-API-Key"
}
```

### Teste B: COM API Key Errada (deve falhar com 403)

```bash
curl -X POST \
  -H "X-API-Key: chave-errada-12345" \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é AI?"}' \
  https://seu-servico.onrender.com/api/v1/ask
```

**Resposta esperada:**
```
HTTP/1.1 403 Forbidden
{
  "detail": "API key inválida"
}
```

### Teste C: COM API Key Correta (deve funcionar com 200)

```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é AI?"}' \
  https://seu-servico.onrender.com/api/v1/ask
```

**Resposta esperada:**
```
HTTP/1.1 200 OK
{
  "answer": "AI é inteligência artificial...",
  ...
}
```

---

## ✅ TESTE 6: Erros e Validação

### Teste A: Pergunta Vazia

```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": ""}' \
  https://seu-servico.onrender.com/api/v1/ask
```

**Resposta esperada:**
```
HTTP/1.1 422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Teste B: Pergunta Muito Longa

```bash
# Pergunta com 3000 caracteres (limite é 2000)
LONG_QUESTION=$(python3 -c "print('x' * 3000)")

curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"$LONG_QUESTION\"}" \
  https://seu-servico.onrender.com/api/v1/ask
```

**Resposta esperada:**
```
HTTP/1.1 422 Unprocessable Entity
Pergunta muito longa (máximo 2000 caracteres)
```

### Teste C: Arquivo Áudio Inválido

```bash
# Criar arquivo fake
echo "isso não é áudio" > fake.txt

# Tentar enviar
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -F "audio_file=@fake.txt" \
  https://seu-servico.onrender.com/api/v1/ask-audio
```

**Resposta esperada:**
```
HTTP/1.1 415 Unsupported Media Type
{
  "detail": "Formato de arquivo não suportado"
}
```

### Teste D: Sem Enviar Arquivo de Áudio

```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  https://seu-servico.onrender.com/api/v1/ask-audio
```

**Resposta esperada:**
```
HTTP/1.1 400 Bad Request
{
  "detail": "Nenhum arquivo de áudio foi enviado"
}
```

---

## 🤖 Script Automático: TESTE TUDO

Salve isso em um arquivo chamado `teste_completo.py`:

```python
#!/usr/bin/env python3
"""
Script para testar TODAS as funcionalidades no Render
Uso: python teste_completo.py https://seu-servico.onrender.com
"""

import requests
import sys
import json

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

def print_ok(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_fail(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

# Verificar argumentos
if len(sys.argv) < 2:
    print("Uso: python teste_completo.py <URL>")
    print("Exemplo: python teste_completo.py https://seu-servico.onrender.com")
    sys.exit(1)

BASE_URL = sys.argv[1].rstrip('/')
API_KEY = "metaverso-secret-key-2026"

print(f"{Colors.BOLD}🧪 TESTE COMPLETO DA API{Colors.END}")
print(f"URL: {BASE_URL}")
print(f"API Key: {API_KEY[:10]}...")

# ============================================
# TESTE 1: Health Check
# ============================================
print_header("TESTE 1: Health Check")
try:
    response = requests.get(f"{BASE_URL}/api/v1/health", timeout=15)
    if response.status_code == 200:
        data = response.json()
        print_ok(f"Status HTTP: {response.status_code}")
        print_ok(f"API Status: {data.get('status')}")
        print_ok(f"RAG Inicializado: {data.get('rag_initialized')}")
    else:
        print_fail(f"Status HTTP: {response.status_code}")
except Exception as e:
    print_fail(f"Erro: {e}")

# ============================================
# TESTE 2: Info
# ============================================
print_header("TESTE 2: Info da API")
try:
    response = requests.get(f"{BASE_URL}/api/v1/info", timeout=15)
    if response.status_code == 200:
        data = response.json()
        print_ok(f"Status HTTP: {response.status_code}")
        print_ok(f"API: {data.get('name')}")
        print_ok(f"Versão: {data.get('version')}")
        print(f"  Embedding Model: {data.get('models', {}).get('embedding')}")
        print(f"  LLM: {data.get('models', {}).get('llm')}")
    else:
        print_fail(f"Status HTTP: {response.status_code}")
except Exception as e:
    print_fail(f"Erro: {e}")

# ============================================
# TESTE 3: Autenticação (sem key)
# ============================================
print_header("TESTE 3: Autenticação (SEM API KEY)")
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/ask",
        json={"question": "Teste"},
        timeout=15
    )
    if response.status_code == 403:
        print_ok(f"Corretamente rejeitado com 403")
        print(f"  Mensagem: {response.json().get('detail')}")
    else:
        print_fail(f"Deveria ser 403, mas foi {response.status_code}")
except Exception as e:
    print_fail(f"Erro: {e}")

# ============================================
# TESTE 4: Pergunta Simples
# ============================================
print_header("TESTE 4: POST /ask (Pergunta em Texto)")
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/ask",
        headers={"X-API-Key": API_KEY},
        json={"question": "O que é inteligência artificial?"},
        timeout=20
    )
    
    if response.status_code == 200:
        data = response.json()
        print_ok(f"Status HTTP: {response.status_code}")
        print_ok(f"Resposta recebida")
        print(f"  Tamanho: {len(data.get('answer', ''))} caracteres")
        print(f"  Confiança: {data.get('confidence', 0):.0%}")
        print(f"  Tempo: {data.get('processing_time_ms', 0):.0f}ms")
        print(f"  Sources: {len(data.get('sources', []))} documentos")
        
        if data.get('answer'):
            preview = data['answer'][:100]
            print(f"  Preview: {preview}...")
    else:
        print_fail(f"Status HTTP: {response.status_code}")
        print(f"  Resposta: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print_fail("Timeout (>20s) - API está lenta")
except Exception as e:
    print_fail(f"Erro: {e}")

# ============================================
# TESTE 5: Validação (pergunta vazia)
# ============================================
print_header("TESTE 5: Validação (Pergunta Vazia)")
try:
    response = requests.post(
        f"{BASE_URL}/api/v1/ask",
        headers={"X-API-Key": API_KEY},
        json={"question": ""},
        timeout=15
    )
    
    if response.status_code == 422:
        print_ok(f"Corretamente rejeitado com 422")
        print(f"  Validação funcionando!")
    else:
        print_fail(f"Deveria ser 422, mas foi {response.status_code}")
except Exception as e:
    print_fail(f"Erro: {e}")

# ============================================
# TESTE 6: Áudio (se houver arquivo)
# ============================================
print_header("TESTE 6: POST /ask-audio (Processamento de Áudio)")
try:
    import os
    
    # Procurar arquivo de teste
    audio_file = None
    for ext in ['mp3', 'wav', 'ogg', 'm4a']:
        if os.path.exists(f"test_audio.{ext}"):
            audio_file = f"test_audio.{ext}"
            break
    
    if audio_file and os.path.exists(audio_file):
        with open(audio_file, 'rb') as f:
            files = {'audio_file': f}
            response = requests.post(
                f"{BASE_URL}/api/v1/ask-audio",
                headers={"X-API-Key": API_KEY},
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print_ok(f"Status HTTP: {response.status_code}")
            print_ok(f"Áudio processado!")
            print(f"  Transcrito: {data.get('audio_transcribed')}")
            print(f"  Confiança: {data.get('confidence', 0):.0%}")
            print(f"  Tempo: {data.get('processing_time_ms', 0):.0f}ms")
        else:
            print_fail(f"Status HTTP: {response.status_code}")
    else:
        print(f"{Colors.YELLOW}⚠️  Nenhum arquivo de áudio encontrado (pulando teste){Colors.END}")
        
except requests.exceptions.Timeout:
    print_fail("Timeout (>30s)")
except Exception as e:
    print_fail(f"Erro: {e}")

# ============================================
# RESUMO
# ============================================
print_header("RESUMO")
print(f"""
Se todos os testes passaram (✅):
  → Sua API está funcionando perfeitamente!
  → Pode usar em produção!

Se algum falhou (❌):
  → Veja a seção Troubleshooting
  → Ou verifique os logs do Render
""")

print(f"Testes concluídos! {Colors.GREEN}✨{Colors.END}\n")
```

### Como usar o script:

```bash
# 1. Salvar como teste_completo.py
# 2. Executar:

python teste_completo.py https://seu-servico.onrender.com

# Exemplo real:
python teste_completo.py https://ic-metaverso-rag-api.onrender.com
```

**Saída esperada:**
```
============================================================
  TESTE 1: Health Check
============================================================

✅ Status HTTP: 200
✅ API Status: healthy
✅ RAG Inicializado: true

============================================================
  TESTE 2: Info da API
============================================================

✅ Status HTTP: 200
✅ API: IC Metaverso RAG API
✅ Versão: 1.0.0
  Embedding Model: intfloat/multilingual-e5-small
  LLM: Groq - mixtral-8x7b-32768

...

RESUMO

Se todos os testes passaram (✅):
  → Sua API está funcionando perfeitamente!
  → Pode usar em produção!
```

---

## 🐛 Troubleshooting

### Erro: "Connection refused" ou "Connection timeout"

```
❌ Problema: Não consegue conectar à URL
✅ Solução:
   1. Copie a URL correta do Dashboard Render
   2. Verifique se o serviço está rodando
   3. Espere 1-2 minutos se foi deployado recentemente
   4. Verifique os logs: Dashboard → Logs
```

### Erro: "404 Not Found"

```
❌ Problema: Endpoint não existe
✅ Solução:
   1. Verifique a URL:
      /api/v1/health       ✅
      /api/v1/info         ✅
      /api/v1/ask          ✅
      /api/v1/ask-audio    ✅
   2. Certifique-se de usar /api/v1/ (não /api/)
```

### Erro: "403 Forbidden"

```
❌ Problema: API Key errada ou faltando
✅ Solução:
   1. Adicionar header: -H "X-API-Key: metaverso-secret-key-2026"
   2. Verifique se a chave está correta
   3. Se mudou a chave, atualize em Render:
      Dashboard → Seu Serviço → Environment → API_KEY
```

### Erro: "500 Internal Server Error"

```
❌ Problema: Erro no servidor
✅ Solução:
   1. Verifique os logs:
      Dashboard → Seu Serviço → Logs
   2. Procure por "ERROR" ou exceções
   3. Problemas comuns:
      - GROQ_API_KEY não configurada
      - ChromaDB vazio (sem documentos ingeridos)
      - Groq API quota excedida
```

### Erro: "Timeout" (requisição demora >30s)

```
❌ Problema: API está muito lenta
✅ Solução:
   1. Normal no Render Free Tier (pode demorar 5-10s)
   2. Aumente o timeout:
      curl --max-time 60 ...
   3. Para produção, considere upgradar para Paid
```

### Erro: "GROQ_API_KEY not found"

```
❌ Problema: Chave Groq não está configurada
✅ Solução:
   1. Vá a: Dashboard Render → Seu Serviço → Environment
   2. Adicione nova variável:
      Key: GROQ_API_KEY
      Value: sua_chave_aqui
   3. Faça re-deploy (ou será aplicado na próxima vez)
   4. Obter chave em: https://console.groq.com
```

### Erro: "RAG not initialized"

```
❌ Problema: ChromaDB não foi inicializado
✅ Solução:
   1. Certifique-se que documentos foram ingeridos
   2. Localmente:
      python -m app.ingest ingest
   3. Em produção (Render):
      - Usar execução remota SSH, ou
      - Re-fazer o deploy com documentos já na pasta Data/
```

---

## ✅ Checklist Final

### Antes de Fazer Deploy

- [ ] Todos os testes passam localmente
- [ ] API Key configurada no .env
- [ ] Groq API Key configurada no .env
- [ ] Documentos estão em ./Data/
- [ ] ChromaDB foi inicializado (ran `ingest`)

### Após Deploy no Render

- [ ] Serviço aparece como "Live" no Dashboard
- [ ] Health check retorna 200
- [ ] Info endpoint retorna dados corretos
- [ ] Pergunta em texto retorna resposta
- [ ] (Opcional) Áudio funciona
- [ ] Segurança: sem key retorna 403
- [ ] Validação: entrada inválida retorna 422

### Testes de Carga (Opcional)

```bash
# Testar 10 requisições simultâneas
for i in {1..10}; do
  curl -X POST \
    -H "X-API-Key: metaverso-secret-key-2026" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}' \
    https://seu-servico.onrender.com/api/v1/ask &
done
wait
```

### Performance Esperada

| Operação | Tempo Esperado |
|----------|----------------|
| Health Check | <100ms |
| Info | <100ms |
| Pergunta (1ª) | 5-15s (Render Free) |
| Pergunta (próximas) | 2-5s |
| Áudio | 5-10s |

---

## 📞 Ajuda Adicional

Se algo não funciona:

1. **Verifique os logs do Render:**
   - Dashboard → Seu Serviço → Logs
   - Procure por mensagens de erro

2. **Rode os testes localmente:**
   - Se funciona local mas não em produção, problema é no deploy

3. **Tente reproduzir o erro:**
   - Execute o mesmo teste 3x
   - Veja se é intermitente ou consistente

4. **Reinicie o serviço:**
   - Dashboard → Seu Serviço → Manual Deploy

---

**Sucesso! Se todos os testes passarem, sua API está pronta para produção! 🚀**
