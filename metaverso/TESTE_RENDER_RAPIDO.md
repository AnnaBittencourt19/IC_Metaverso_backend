# 🚀 TESTE NO RENDER - SUPER SIMPLES

## 📌 O Essencial (3 passos)

### 1. Obter URL do Render
```
Dashboard Render → Seu Serviço → URL
Exemplo: https://ic-metaverso-rag-api.onrender.com
```

### 2. Testar Health (seu navegador)
```
https://seu-servico.onrender.com/api/v1/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "rag_initialized": true
}
```

### 3. Testar com cURL (terminal)

**Terminal:**
```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é 6G?"}' \
  https://seu-servico.onrender.com/api/v1/ask
```

Deve retornar 200 OK com resposta.

---

## 🎯 Se der erro...

| Erro | Solução |
|------|---------|
| 404 Not Found | URL incorreta - copie do dashboard |
| 403 Forbidden | API Key errada - verifique `.env` |
| 500 Server Error | Verifique logs: Dashboard → Logs |
| Timeout (>30s) | Render free tier é lento - esperado |

---

## 📊 Teste Completo (Python)

```bash
python test_render.py https://seu-servico.onrender.com
```

Vai testar:
- ✅ Health
- ✅ Info
- ✅ Ask (sem key) → 403
- ✅ Ask (com key) → 200
- ✅ Ask-audio (se tiver arquivo)

---

## 🎤 Testar Áudio

```bash
# 1. Criar áudio de teste
python3 << 'EOF'
import pyttsx3
engine = pyttsx3.init()
engine.save_to_file("O que é 6G", "test.mp3")
engine.runAndWait()
EOF

# 2. Enviar
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -F "audio_file=@test.mp3" \
  https://seu-servico.onrender.com/api/v1/ask-audio
```

---

## ✅ Está funcionando quando você ver:

```
Status: 200
Response: "6G é a próxima geração..."
Docs used: 2
Confidence: alta
Timestamp: 2026-04-08T...
```

---

## 📚 Documentação Completa

Veja `docs/TESTE_RENDER.md` para detalhes completos.

---

**Pronto! 🎉**
