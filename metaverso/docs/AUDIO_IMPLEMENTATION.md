# 🎤 Implementação de Suporte a Áudio (Voice Input) - Documentação

## 📋 Visão Geral

A API agora suporta processamento de voz. O cliente grava áudio, envia para o servidor, que transcreve com Groq Whisper e processa com RAG, tudo em um único endpoint.

---

## 🔄 Fluxo de Processamento de Áudio

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cliente (Unity)                              │
│                  1. Grava áudio do microfone                    │
│                  2. Salva como arquivo (MP3/WAV/M4A)            │
└──────────────────────┬──────────────────────────────────────────┘
                       │ POST /api/v1/ask-audio + arquivo
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                  Servidor (FastAPI)                             │
│                                                                  │
│  main.py:ask_audio()                                            │
│    1. Valida API Key                                            │
│    2. Valida tipo de arquivo                                    │
│    3. Salva em arquivo temporário                               │
│                ▼                                                │
│    rag.py:process_audio_and_answer()                           │
│    rag.py:transcribe_audio()                                    │
│    1. Envia arquivo para Groq Whisper                          │
│    2. Recebe texto transcrito                                   │
│    3. Passa para hierarchical_search_and_generate()            │
│                ▼                                                │
│    1. Busca documentos relevantes                              │
│    2. Reranking                                                │
│    3. Gera resposta com Groq                                   │
│    4. Formata resposta                                         │
│                                                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ JSON Response (200 OK)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Cliente (Unity)                              │
│                                                                  │
│  Recebe:                                                        │
│  - audio_transcribed: "O que é 6G?"                            │
│  - response: "6G é a próxima geração..."                       │
│  - sources: [docs usados]                                      │
│  - confidence: "alta"                                          │
│  - timestamp: "2026-04-08T14:30:05"                           │
│                                                                  │
│  Exibe na UI:                                                   │
│  - Transcrição do que foi dito                                 │
│  - Resposta do RAG                                             │
│  - Fontes consultadas                                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ O que foi implementado

### 1. **Backend (app/rag.py)**

**Nova Função: `transcribe_audio(audio_file_path: str) → str`**
```python
def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcreve arquivo de áudio usando Groq Whisper
    
    Args:
        audio_file_path: Caminho do arquivo (mp3, wav, m4a, etc)
    
    Returns:
        Texto transcrito em português
    """
```

**Como funciona:**
1. Abre o arquivo de áudio
2. Envia para `Groq().audio.transcriptions.create()`
3. Usa modelo `whisper-large-v3-turbo`
4. Configura idioma como português (`language="pt"`)
5. Retorna texto transcrito

**Nova Função: `process_audio_and_answer(audio_file_path: str) → dict`**
```python
def process_audio_and_answer(audio_file_path: str) -> dict:
    """
    Integra transcrição + RAG
    """
```

**Como funciona:**
1. Chama `transcribe_audio()` para transcrever
2. Passa texto para `hierarchical_search_and_generate()`
3. Adiciona metadados ao resultado
4. Retorna dicionário completo com response + transcrição

---

### 2. **API (app/main.py)**

**Novo Endpoint: `POST /api/v1/ask-audio`**
```python
@app.post("/api/v1/ask-audio", response_model=AudioResponse)
async def ask_audio(
    audio_file: UploadFile = File(...),
    x_api_key: str = Header(None)
) -> AudioResponse:
```

**Funcionalidades:**
- ✅ Requer autenticação via `X-API-Key`
- ✅ Valida tipo de arquivo (MP3, WAV, M4A, FLAC, OGG, etc)
- ✅ Salva arquivo em diretório temporário
- ✅ Chama `process_audio_and_answer()`
- ✅ Formata respostas com `SourceInfo`
- ✅ Limpa arquivo temporário após processamento
- ✅ Tratamento robusto de erros

**Tipos de arquivo suportados:**
```
audio/mpeg          (.mp3)
audio/wav           (.wav)
audio/mp4           (.m4a)
audio/ogg           (.ogg)
audio/flac          (.flac)
audio/webm          (.webm)
audio/x-m4a         (.m4a)
```

**Response Modelo: `AudioResponse`**
```python
class AudioResponse(BaseModel):
    response: str                    # Resposta RAG
    audio_transcribed: str          # Texto transcrito
    sources: List[SourceInfo]       # Docs usados
    docs_used: int                  # Contagem
    timestamp: datetime             # Quando foi processado
    confidence: Optional[str]       # Nível de confiança
    is_audio: bool                  # Flag indicador
```

---

## 📡 Como Usar via cURL

### Testar com arquivo local:
```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -F "audio_file=@/path/to/audio.mp3" \
  http://localhost:8000/api/v1/ask-audio
```

### Resposta esperada:
```json
{
  "response": "6G é a próxima geração de comunicação móvel...",
  "audio_transcribed": "O que é 6G?",
  "sources": [
    {
      "content": "Conteúdo do documento 1...",
      "metadata": {
        "source": "documento1.pdf",
        "page": 5
      }
    }
  ],
  "docs_used": 2,
  "timestamp": "2026-04-08T14:30:05.123456",
  "confidence": "alta",
  "is_audio": true
}
```

---

## 🎮 Como Usar em Unity

### Passo 1: Adicionar classe cliente atualizada
```csharp
public class MetaversoRAGClient : MonoBehaviour
{
    private string askAudioEndpoint => $"{apiUrl}/api/v1/ask-audio";
    
    public IEnumerator AskAudio(string audioFilePath, 
        System.Action<RAGAudioResponse> onSuccess, 
        System.Action<string> onError)
    {
        // Implementação completa em UNITY_INTEGRATION.md
    }
}
```

### Passo 2: Usar em seu manager
```csharp
chatManager.SendAudio("/path/to/audio.mp3");
```

### Passo 3: Adicionar gravação de áudio (opcional)
```csharp
public class VoiceManager : MonoBehaviour
{
    public void StartRecording() => 
        recordedAudio = Microphone.Start(...);
    
    public void StopRecording() {
        Microphone.End(null);
        SavWav.Save("temp_audio", recordedAudio);
        chatManager.SendAudio(audioPath);
    }
}
```

---

## 🔐 Autenticação

Assim como `/api/v1/ask`, o endpoint `/ask-audio` **exige** autenticação:

```
Header: X-API-Key: sua_chave_api
```

Se não fornecer:
```json
{
  "detail": "API key não fornecida no header X-API-Key",
  "error": "forbidden",
  "status_code": 403
}
```

---

## ⚙️ Configuração Necessária

### No `.env`, já temos tudo que precisa:
```
GROQ_API_KEY=xyz...          # Necessário para Whisper
API_KEY=metaverso-secret-key-2026
```

A transcrição de áudio é **gratuita** no plano Groq.

---

## 🧪 Testando

### 1. Gerar um áudio de teste (Python)
```python
import pyttsx3

engine = pyttsx3.init()
engine.save_to_file("O que é 6G?", "test_audio.mp3")
engine.runAndWait()
```

### 2. Enviar para API
```bash
curl -X POST \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -F "audio_file=@test_audio.mp3" \
  http://localhost:8000/api/v1/ask-audio
```

### 3. Verificar resposta
A API deve retornar:
- `audio_transcribed`: "O que é 6G?"
- `response`: Texto com resposta
- `docs_used`: Número de documentos
- `confidence`: Nível de confiança

---

## 🔧 Troubleshooting

### "400 - Tipo de arquivo não suportado"
- Use MP3, WAV, M4A, FLAC ou OGG
- Verifique `Content-Type` do upload

### "403 - API key não fornecida"
- Certifique-se de enviar header `X-API-Key`
- Valide a chave em `.env`

### "Erro ao transcrever áudio"
- Verifique se `GROQ_API_KEY` é válida
- Confirme que o arquivo não está corrompido
- Tente com arquivo diferente

### Áudio muito longo
- Groq Whisper tem limite de duração
- Máximo recomendado: ~30 minutos
- Divida arquivos muito longos

---

## 📊 Performance

**Tempos esperados:**
| Operação | Tempo |
|----------|-------|
| Transcrição (30s áudio) | 2-4s |
| RAG (busca + reranking) | 1-2s |
| Geração (Groq) | 3-5s |
| **Total** | **~8-12s** |

---

## 🔄 Fluxo Técnico Detalhado

### 1. Request chega
```
POST /api/v1/ask-audio
File: audio_file (binary)
Header: X-API-Key
```

### 2. main.py:ask_audio()
```python
# Valida API key
verify_api_key(x_api_key)  # ✓ ou ✗

# Valida tipo
if audio_file.content_type not in allowed_types:
    raise 400

# Salva temp
with tempfile.NamedTemporaryFile() as tmp:
    tmp.write(audio_file.read())
    tmp_path = tmp.name
```

### 3. rag.py:process_audio_and_answer()
```python
# Transcreve
question = transcribe_audio(tmp_path)
# "O que é 6G?"

# Processa
result = hierarchical_search_and_generate(question)
# RAG pipeline completo

# Adiciona metadata
result['audio_transcribed'] = question
result['is_audio'] = True
```

### 4. main.py serializa
```python
response_data = AudioResponse(
    response=result['response'],
    audio_transcribed=question,
    sources=[...],
    docs_used=len(docs),
    confidence=result['confidence'],
    is_audio=True
)
```

### 5. Response é enviado
```json
{
  "response": "...",
  "audio_transcribed": "O que é 6G?",
  ...
}
```

### 6. Cleanup
```python
os.unlink(tmp_path)  # Remove arquivo temporário
```

---

## 📝 Próximas Melhorias (Futuro)

- [ ] Adicionar WebSocket para streaming de resposta
- [ ] Suportar múltiplos idiomas automaticamente
- [ ] Cache de áudios já processados
- [ ] Detecção de qualidade de áudio
- [ ] Compressão de áudio antes de enviar
- [ ] Rate limiting específico para uploads de áudio
- [ ] Logging de métricas (latência, idiomas, etc)

---

## ✅ Checklist

- [x] Função de transcrição implementada
- [x] Endpoint `/ask-audio` criado
- [x] Autenticação adicionada
- [x] Validação de arquivo
- [x] Response model criado
- [x] Tratamento de erros
- [x] Cleanup de temp files
- [x] Documentação em UNITY_INTEGRATION.md
- [x] Exemplos de código C# inclusos
- [x] Suporte a múltiplos formatos de áudio

---

**Documentação criada:** 8 de abril de 2026
**Status:** ✅ Production Ready
