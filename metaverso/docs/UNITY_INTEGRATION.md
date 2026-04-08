# 🎮 Guia de Integração com Unity

## Overview

Este guia explica como integrar a API IC Metaverso RAG em uma aplicação Unity (WebGL, Standalone ou Mobile).

---

## 📋 Pré-requisitos

1. **API rodando** em um servidor acessível
   - Local: `http://localhost:8000`
   - Produção: `https://seu-dominio.com`

2. **API Key**: Solicite ao administrador da API
   - Padrão de desenvolvimento: `metaverso-secret-key-2026`

3. **CORS configurado**: A API permite requisições do seu cliente

---

## 🔐 Autenticação

Todas as requisições para `/api/v1/ask` requerem:

```
Header: X-API-Key: sua_chave_api
```

---

## 📡 Endpoints Disponíveis

### 1. Health Check (Público)
```
GET /api/v1/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-08T12:00:00",
  "rag_initialized": true
}
```

### 2. Informações da API (Público)
```
GET /api/v1/info
```

**Resposta:**
```json
{
  "name": "IC Metaverso RAG API",
  "version": "1.0.0",
  "description": "Sistema RAG otimizado para integração com Unity",
  "endpoints": {
    "health": "/api/v1/health",
    "ask": "/api/v1/ask",
    "docs": "/api/v1/docs"
  }
}
```

### 3. Fazer uma Pergunta (Autenticado)
```
POST /api/v1/ask
```

**Headers:**
```
X-API-Key: sua_chave_api
Content-Type: application/json
```

**Corpo (Request):**
```json
{
  "question": "O que é 6G?"
}
```

**Resposta (200 OK):**
```json
{
  "response": "6G é a próxima geração de tecnologia de comunicação móvel...",
  "sources": [
    {
      "content": "Documento 1 - Conteúdo...",
      "metadata": {
        "source": "documento1.pdf",
        "page": 5
      }
    },
    {
      "content": "Documento 2 - Conteúdo...",
      "metadata": {
        "source": "documento2.pdf",
        "page": 12
      }
    }
  ],
  "docs_used": 2,
  "timestamp": "2026-04-08T12:00:00",
  "confidence": "alta"
}
```

**Erros possíveis:**
- `403 Forbidden`: API key não fornecida ou inválida
- `500 Internal Server Error`: Erro ao processar a pergunta

### 4. Fazer uma Pergunta via Áudio (Autenticado) 🎤
```
POST /api/v1/ask-audio
```

**Headers:**
```
X-API-Key: sua_chave_api
Content-Type: multipart/form-data
```

**Corpo (Request):**
- `audio_file`: Arquivo de áudio (MP3, WAV, M4A, FLAC, OGG, etc)

**Fluxo:**
1. Cliente envia arquivo de áudio
2. Servidor transcreve com Groq Whisper (português)
3. Servidor processa o texto com RAG
4. Retorna resposta + transcrição

**Resposta (200 OK):**
```json
{
  "response": "6G é a próxima geração de tecnologia de comunicação móvel...",
  "audio_transcribed": "O que é 6G?",
  "sources": [
    {
      "content": "Documento 1 - Conteúdo...",
      "metadata": {
        "source": "documento1.pdf",
        "page": 5
      }
    }
  ],
  "docs_used": 2,
  "timestamp": "2026-04-08T12:00:05",
  "confidence": "alta",
  "is_audio": true
}
```

**Erros possíveis:**
- `403 Forbidden`: API key não fornecida ou inválida
- `400 Bad Request`: Tipo de arquivo não suportado
- `500 Internal Server Error`: Erro ao transcrever ou processar

---

## 🎯 Exemplo de Integração em Unity (C#)

### 1. Criar uma classe para a API

```csharp
using UnityEngine;
using System.Collections;
using UnityEngine.Networking;
using System.Text;
using Newtonsoft.Json;

[System.Serializable]
public class DocumentSource
{
    public string content;
    public object metadata;
}

[System.Serializable]
public class RAGResponse
{
    public string response;
    public DocumentSource[] sources;
    public int docs_used;
    public string timestamp;
    public string confidence;
}

[System.Serializable]
public class RAGAudioResponse
{
    public string response;
    public string audio_transcribed;
    public DocumentSource[] sources;
    public int docs_used;
    public string timestamp;
    public string confidence;
    public bool is_audio;
}

[System.Serializable]
public class RAGQuestion
{
    public string question;
}

public class MetaversoRAGClient : MonoBehaviour
{
    [SerializeField]
    private string apiUrl = "http://localhost:8000";
    
    [SerializeField]
    private string apiKey = "metaverso-secret-key-2026";
    
    private string askEndpoint => $"{apiUrl}/api/v1/ask";
    private string askAudioEndpoint => $"{apiUrl}/api/v1/ask-audio";
    private string healthEndpoint => $"{apiUrl}/api/v1/health";

    /// <summary>
    /// Faz uma pergunta para o RAG
    /// </summary>
    public IEnumerator AskQuestion(string question, System.Action<RAGResponse> onSuccess, System.Action<string> onError)
    {
        RAGQuestion questionData = new RAGQuestion { question = question };
        string jsonBody = JsonConvert.SerializeObject(questionData);

        using (UnityWebRequest request = new UnityWebRequest(askEndpoint, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            
            // Headers
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("X-API-Key", apiKey);

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    RAGResponse response = JsonConvert.DeserializeObject<RAGResponse>(request.downloadHandler.text);
                    onSuccess?.Invoke(response);
                }
                catch (System.Exception ex)
                {
                    onError?.Invoke($"Erro ao desserializar resposta: {ex.Message}");
                }
            }
            else
            {
                onError?.Invoke($"Erro HTTP {request.responseCode}: {request.error}");
            }
        }
    }

    /// <summary>
    /// Verifica se a API está disponível
    /// </summary>
    public IEnumerator CheckHealth(System.Action<bool> onComplete)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(healthEndpoint))
        {
            yield return request.SendWebRequest();
            bool isHealthy = request.result == UnityWebRequest.Result.Success;
            onComplete?.Invoke(isHealthy);
        }
    }

    /// <summary>
    /// Envia um arquivo de áudio para ser transcrito e processado
    /// </summary>
    public IEnumerator AskAudio(string audioFilePath, System.Action<RAGAudioResponse> onSuccess, System.Action<string> onError)
    {
        // Verificar se arquivo existe
        if (!System.IO.File.Exists(audioFilePath))
        {
            onError?.Invoke($"Arquivo de áudio não encontrado: {audioFilePath}");
            yield break;
        }

        // Ler arquivo de áudio
        byte[] audioData = System.IO.File.ReadAllBytes(audioFilePath);
        string fileName = System.IO.Path.GetFileName(audioFilePath);

        using (UnityWebRequest request = new UnityWebRequest(askAudioEndpoint, "POST"))
        {
            // Criar form data com arquivo
            List<IMultipartFormSection> formData = new List<IMultipartFormSection>();
            formData.Add(new MultipartFormFileSection("audio_file", audioData, fileName, "audio/mpeg"));

            request.uploadHandler = new UploadHandlerRaw(UnityWebRequest.SerializeFormSections(formData, UnityWebRequest.GenerateBoundary()));
            request.downloadHandler = new DownloadHandlerBuffer();

            // Headers
            string boundary = UnityWebRequest.GenerateBoundary();
            request.SetRequestHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
            request.SetRequestHeader("X-API-Key", apiKey);

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    RAGAudioResponse response = JsonConvert.DeserializeObject<RAGAudioResponse>(request.downloadHandler.text);
                    onSuccess?.Invoke(response);
                }
                catch (System.Exception ex)
                {
                    onError?.Invoke($"Erro ao desserializar resposta: {ex.Message}");
                }
            }
            else
            {
                onError?.Invoke($"Erro HTTP {request.responseCode}: {request.error}");
            }
        }
    }
}
```

### 2. Usar a API em um script

```csharp
public class ChatManager : MonoBehaviour
{
    private MetaversoRAGClient ragClient;

    void Start()
    {
        ragClient = GetComponent<MetaversoRAGClient>();
    }

    public void SendQuestion(string question)
    {
        StartCoroutine(ragClient.AskQuestion(
            question,
            onSuccess: HandleSuccess,
            onError: HandleError
        ));
    }

    public void SendAudio(string audioFilePath)
    {
        StartCoroutine(ragClient.AskAudio(
            audioFilePath,
            onSuccess: HandleAudioSuccess,
            onError: HandleError
        ));
    }

    private void HandleSuccess(RAGResponse response)
    {
        Debug.Log($"Resposta: {response.response}");
        Debug.Log($"Documentos usados: {response.docs_used}");
        Debug.Log($"Confiança: {response.confidence}");
        
        // Mostrar resposta na UI
        DisplayResponse(response);
    }

    private void HandleAudioSuccess(RAGAudioResponse response)
    {
        Debug.Log($"Áudio transcrito: {response.audio_transcribed}");
        Debug.Log($"Resposta: {response.response}");
        Debug.Log($"Documentos usados: {response.docs_used}");
        Debug.Log($"Confiança: {response.confidence}");
        
        // Mostrar resposta e transcrição na UI
        DisplayAudioResponse(response);
    }

    private void HandleError(string error)
    {
        Debug.LogError($"Erro: {error}");
        // Mostrar erro na UI
    }

    private void DisplayResponse(RAGResponse response)
    {
        // Implementar lógica de exibição
        // Ex: atualizar texto em Canvas, mostrar animação, etc.
    }

    private void DisplayAudioResponse(RAGAudioResponse response)
    {
        // Implementar lógica de exibição para áudio
        // Ex: mostrar transcrição + resposta em Canvas
    }
}

### 3. Exemplo com Gravação de Áudio

```csharp
public class VoiceManager : MonoBehaviour
{
    private AudioClip recordedAudio;
    private string audioSavePath;
    
    void Start()
    {
        // Caminho onde salvar o áudio
        audioSavePath = Application.persistentDataPath + "/temp_audio.wav";
    }
    
    public void StartRecording()
    {
        // Começar a gravar áudio do microfone
        recordedAudio = Microphone.Start(null, false, 30, 16000);
        Debug.Log("Gravação iniciada...");
    }
    
    public void StopRecording()
    {
        // Parar gravação
        Microphone.End(null);
        
        // Salvar como WAV
        SavWav.Save("temp_audio", recordedAudio);
        
        Debug.Log("Gravação salva em: " + audioSavePath);
        
        // Enviar para API
        SendRecordedAudio();
    }
    
    private void SendRecordedAudio()
    {
        ChatManager chatManager = GetComponent<ChatManager>();
        chatManager.SendAudio(audioSavePath);
    }
}
```

---

## 🌐 CORS - Configuração para WebGL

Se estiver usando Unity WebGL, certifique-se de que:

1. A API tem CORS habilitado (já está)
2. Seu cliente está na lista de `allowed_origins`

**Modificar `.env` se necessário:**
```
UNITY_ORIGIN=https://seu-jogo.com
```

---

## 🚀 Deployment

### Local
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Produção (Render/Docker)
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 📊 Rate Limiting (Futuro)

Para evitar abuso, considere adicionar rate limiting:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/ask")
@limiter.limit("10/minute")
async def ask(...):
    ...
```

---

## 🔍 Troubleshooting

### "403 Forbidden - API key não fornecida"
- Verifique se está enviando o header `X-API-Key`
- Valide a chave fornecida

### "CORS error em WebGL"
- Verifique se sua origem está em `allowed_origins`
- Teste com `UNITY_ORIGIN=*` temporariamente (não recomendado em produção)

### "500 Internal Server Error"
- Verifique os logs do servidor
- Certifique-se de que o ChromaDB foi inicializado
- Verifique se a GROQ_API_KEY é válida

### Lentidão
- O RAG faz embedding e busca - é esperado latência de 2-5 segundos
- Considere cache ou streaming de respostas

---

## 📚 Documentação Adicional

- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

---

## ✅ Checklist de Integração

- [ ] API está rodando e acessível
- [ ] API key foi obtida
- [ ] CORS está configurado para sua origem
- [ ] Classe `MetaversoRAGClient` foi criada no projeto Unity
- [ ] Implementou tratamento de sucesso e erro
- [ ] Testou endpoint `/api/v1/health` primeiro
- [ ] Testou endpoint `/api/v1/ask` com uma pergunta simples
- [ ] UI foi criada para exibir respostas
- [ ] Tratamento de loading foi implementado
- [ ] Testes em produção foram feitos

---

**Dúvidas?** Entre em contato com o time de desenvolvimento.
