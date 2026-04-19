# 🎮 O PROJETO METAVERSO - EXPLICADO DE FORMA SIMPLES

---

## 🤔 O que é?

Imagine que você tem um **assistente de IA** que:
- 📚 Lê vários documentos (PDFs, textos, etc)
- 🧠 Aprende com eles
- 💬 Responde suas perguntas usando o que aprendeu
- 🎤 **NOVO:** Também entende áudio! Você fala e ele responde

É basicamente um **Google, mas customizado para seus documentos**.

---

## 🎯 Para que serve?

Você pode fazer isso:

### Exemplo 1: Pergunta por texto
```
Você: "O que é machine learning?"
IA:   "Machine learning é... [resposta inteligente]"
```

### Exemplo 2: Pergunta por áudio
```
Você fala no microfone: "O que é machine learning?"
IA ouve, entende e responde: "Machine learning é..."
```

### Exemplo 3: Dentro de um jogo (Unity)
```
Jogador fala no jogo
↓
Servidor recebe a voz
↓
IA processa
↓
Resposta aparece no jogo
```

---

## 🧩 Como Funciona (Versão Super Simples)

### Passo 1: Você dá documentos
```
Você coloca PDFs em uma pasta → Servidor lê tudo
```

### Passo 2: Servidor aprende
```
Servidor processa os documentos
↓
Transforma em "números" que a IA entende
↓
Guarda em um banco de dados especial
```

### Passo 3: Você faz uma pergunta
```
Você: "O que é X?"
↓
Servidor procura nos documentos (tipo Google)
↓
Encontra as respostas mais relevantes
↓
Usa IA para gerar uma resposta bonita
↓
Você recebe a resposta
```

### Passo 4: Pronto!
```
Tudo acontece em 2-3 segundos
```

---

## 🏗️ Os "Pedaços" do Projeto

### 1. **A API** (main.py)
É como um "garçom" que recebe seus pedidos:

```
Você fala: "Quero saber sobre X"
Garçom:    "OK, vou perguntar ao chefe"
Chefe (IA): "A resposta é Y"
Garçom:    "Aqui está: Y"
Você:      "Obrigado!"
```

**O que ela faz:**
- Recebe perguntas
- Valida se você tem permissão (chave secreta)
- Passa para o "chefe" (RAG)
- Devolve a resposta

### 2. **O Chefe (RAG)** (rag.py)
É o "cérebro" do projeto:

```
Pergunta recebida
↓
Procura nos documentos
↓
Encontra as respostas mais parecidas
↓
Ordena por qualidade
↓
Usa IA para gerar uma resposta
↓
Retorna ao garçom
```

**O que ele faz:**
- Busca em vários documentos
- Ordena por relevância
- Gera respostas bonitas
- Calcula confiança (quão certo ele está)

### 3. **O Banco de Dados** (ChromaDB)
É como um "dicionário mágico":

```
Documento normal:     "Machine learning é..."
Versão mágica:        [0.234, 0.891, 0.123, ...]  (números)

Quando você pergunta:  "O que é ML?"
Versão mágica:        [0.225, 0.890, 0.120, ...]
                      ↓
                      "Muito parecido! Encontrei!"
```

**O que ele faz:**
- Guarda documentos em formato especial
- Busca rápido por similaridade
- Economiza espaço

---

## 💬 Os "Endpoints" (Pontos de Entrada)

Pense em endpoints como "botões" que você pode apertar:

### Botão 1: "Eu estou vivo?"
```
Você clica: GET http://localhost:8000/
Servidor:  "Sim, estou funcionando!"
```

### Botão 2: "Me diz uma pergunta de texto"
```
Você clica: POST http://localhost:8000/api/v1/ask
Você envia: "O que é RAG?"
Servidor:  "RAG é um sistema que... [resposta longa]"
```

### Botão 3: "Me diz uma pergunta por áudio"
```
Você clica: POST http://localhost:8000/api/v1/ask-audio
Você envia: Arquivo de áudio da sua voz
Servidor:  "Você perguntou: [transcrição]"
           "A resposta é: [resposta longa]"
```

---

## 🔐 Segurança (Por que precisa de senha?)

```
Sem segurança:
  Qualquer um na internet pode fazer perguntas
  → Seu servidor quebra
  → Alguém usa sua IA ilimitadamente
  → Você paga muito

Com segurança:
  Você dá uma "senha" (chave) para seus amigos
  Só quem tem a senha pode fazer perguntas
  → Seu servidor está protegido
```

**Como usar:**
```
curl -H "X-API-Key: SUA_SENHA_AQUI" http://localhost:8000/api/v1/ask
```

---

## 🎤 Como o Áudio Funciona

### Passo a passo:

```
1. Você grava um áudio
   "O que é machine learning?"

2. Envia para o servidor
   POST /api/v1/ask-audio
   [arquivo.mp3]

3. Servidor usa IA especial (Whisper)
   Converte áudio em texto
   "O que é machine learning?"

4. Processa normalmente
   (Como se você tivesse digitado)

5. Devolve tudo:
   - O que você falou (transcrito)
   - A resposta
   - Confiança (0-100%)
```

---

## 📦 O que Você Precisa Para Começar

### 1. **Um Computador** (ou servidor)
```
Windows, Mac, ou Linux
```

### 2. **Python 3.11**
```
Tipo de linguagem que faz o servidor funcionar
```

### 3. **Chave da API Groq** (Grátis!)
```
Groq = Empresa de IA
Você se registra, pega a chave
Coloca no projeto
```

### 4. **Seus Documentos**
```
PDFs, TXTs, qualquer coisa
Coloca em uma pasta
```

---

## 🚀 Começar (5 Passos Simples)

### Passo 1: Baixar o Projeto
```bash
git clone <link-do-projeto>
cd metaverso
```

### Passo 2: Criar um "Ambiente Isolado"
```bash
python3 -m venv venv
source venv/bin/activate
```

**Por quê?** Para não misturar as dependências do projeto com o resto do computador.

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

**Por quê?** O projeto precisa de libraries externas para funcionar.

### Passo 4: Configurar Chaves
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas chaves
# GROQ_API_KEY=sua_chave_aqui
# API_KEY=sua_senha_aqui
```

### Passo 5: Colocar Documentos
```bash
# Copiar seus PDFs para:
./Data/

# Depois processar:
python -m app.ingest ingest
```

### Passo 6: Iniciar!
```bash
uvicorn app.main:app --reload
```

**Pronto!** Seu servidor está rodando em `http://localhost:8000`

---

## 🧪 Testar Se Funciona

### Teste 1: Health Check (Tá funcionando?)
```bash
curl http://localhost:8000/api/v1/health
```

Resposta esperada:
```json
{"status": "healthy"}
```

### Teste 2: Info (Me diz sobre você)
```bash
curl http://localhost:8000/api/v1/info
```

### Teste 3: Fazer uma Pergunta
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "X-API-Key: metaverso-secret-key-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "O que você é?"}'
```

Resposta esperada:
```json
{
  "answer": "Eu sou um assistente de IA...",
  "sources": ["documento.pdf"],
  "confidence": 0.95,
  "processing_time_ms": 2345.67
}
```

---

## 🎮 Usar em um Jogo (Unity)

### Código Super Simples em C#

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class ChatBot : MonoBehaviour
{
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            // Quando apertar espaço, fazer pergunta
            AskQuestion("O que você faz?");
        }
    }

    void AskQuestion(string question)
    {
        StartCoroutine(SendRequest(question));
    }

    IEnumerator SendRequest(string question)
    {
        // URL do seu servidor
        string url = "http://localhost:8000/api/v1/ask";
        
        // Dados a enviar
        string json = "{\"question\": \"" + question + "\"}";
        
        // Criar request
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        request.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json));
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        request.SetRequestHeader("X-API-Key", "metaverso-secret-key-2026");
        
        // Enviar
        yield return request.SendWebRequest();
        
        // Receber resposta
        if (request.result == UnityWebRequest.Result.Success)
        {
            // Pegar a resposta
            string response = request.downloadHandler.text;
            Debug.Log("Resposta: " + response);
            
            // Aqui você trata a resposta
            // Pode exibir em um painel, fazer o personagem falar, etc
        }
        else
        {
            Debug.LogError("Erro: " + request.error);
        }
    }
}
```

**Como usar no jogo:**
1. Adicionar esse script a um GameObject
2. Quando jogador pressiona espaço, faz uma pergunta
3. Servidor responde
4. Você faz o que quiser com a resposta (mostrar na tela, falar, etc)

---

## 📚 Tipo de Resposta Que Você Recebe

### Resposta Simples
```json
{
  "answer": "Machine learning é um tipo de inteligência artificial que aprende com dados.",
  "sources": ["documento1.pdf - página 5"],
  "confidence": 0.87,
  "timestamp": "2026-04-18T10:30:45Z",
  "processing_time_ms": 2345.67
}
```

**O que significa:**
- `answer`: A resposta que o AI gerou
- `sources`: Onde ele tirou essa resposta (qual documento)
- `confidence`: Quão certo ele está (0 = não sabe, 1 = tem certeza)
- `timestamp`: Quando foi processado
- `processing_time_ms`: Quanto tempo levou

### Resposta com Áudio
```json
{
  "audio_transcribed": "O que é machine learning?",
  "answer": "Machine learning é...",
  "sources": ["documento1.pdf - página 5"],
  "confidence": 0.87,
  "timestamp": "2026-04-18T10:30:45Z",
  "processing_time_ms": 3456.78
}
```

**O que significa:**
- `audio_transcribed`: O que você falou, em texto
- (resto é igual)

---

## ⚡ Por Que Isso é Rápido?

Normalmente, fazer uma IA gerar resposta demora muito.

**Com RAG é rápido porque:**

```
❌ Sem RAG (lento):
   IA lê TODO documento
   IA pensa muito
   → 10-20 segundos

✅ Com RAG (rápido):
   IA procura só as partes relevantes
   IA lê pouquinho
   IA pensa pouco
   → 2-3 segundos
```

---

## 🔍 O que Cada Arquivo Faz

```
/app/main.py          → O "garçom" (recebe pedidos)
/app/rag.py           → O "chefe" (faz as respostas)
/app/config.py        → As "regras da casa" (configurações)
/app/ingest.py        → Ensina o IA sobre novos documentos

/Data/                → Seus documentos (PDFs, etc)
/chroma_db_export/    → "Memória" da IA (onde ela guarda o que aprendeu)

/tests/               → Testes (certificar que tudo funciona)
/docs/                → Documentação mais detalhada
```

---

## 🐛 Erros Comuns

### Erro: "API key não fornecida"
```
Você: "Fiz uma pergunta mas deu erro"
Motivo: Você esqueceu de enviar a senha
Solução: Adicione -H "X-API-Key: SUA_CHAVE"
```

### Erro: "GROQ_API_KEY não configurada"
```
Você: "Servidor não inicia"
Motivo: Você não adicionou a chave Groq no .env
Solução: Adicione GROQ_API_KEY=sua_chave no arquivo .env
```

### Erro: "Nenhum documento encontrado"
```
Você: "Perguntei mas disse 'não encontrei resposta'"
Motivo: Você não adicionou documentos em ./Data/ ou não rodou ingest
Solução: 
  1. Coloque PDFs em ./Data/
  2. Execute: python -m app.ingest ingest
```

### Erro: "Port 8000 is already in use"
```
Você: "Não consigo iniciar o servidor"
Motivo: Outro programa está usando a porta 8000
Solução: 
  uvicorn app.main:app --port 8001
  (usa outra porta)
```

---

## 📊 Resumo em Números

```
💬 Endpoints:          5
📚 Documentação:       3000+ linhas
🧪 Testes:            1000+ linhas
⚙️ Linhas de código:   2500+
🚀 Tempo de resposta:  2-3 segundos
🔒 Segurança:         Protegida com chave
🌍 Idiomas:           Multilíngue (português, inglês, etc)
```

---

## 🎯 Casos de Uso Reais

### Caso 1: Jogo Educativo
```
Aluno:    "O que é fotossíntese?"
IA:       "Fotossíntese é..." (baseado em textos da escola)
Aluno:    "Legal, entendi!"
```

### Caso 2: Suporte ao Cliente
```
Cliente:  "Como resetar minha senha?"
IA:       "Para resetar sua senha..." (baseado em manual)
Cliente:  "Pronto, funcionou!"
```

### Caso 3: Assistente de Pesquisa
```
Pesquisador: "Quais são os tipos de IA?"
IA:          "Os tipos são..." (baseado em papers científicos)
Pesquisador: "Perfeito para minha tese!"
```

### Caso 4: Guia Turístico Virtual
```
Turista: "O que ver em SP?"
IA:      "Em SP você tem..." (baseado em guias)
Turista: "Vou visitar!"
```

---

## 🚀 Próximo Passo: Colocar em Produção

### Quando estiver pronto, você pode:

1. **Colocar em um servidor** (Render, AWS, Google Cloud, etc)
2. **Deixar disponível 24/7**
3. **Pessoas acessam de qualquer lugar**
4. **Seu jogo acessa de qualquer lugar**

**É como:**
```
Seu computador pessoal
         ↓
        (upload)
         ↓
Servidor profissional
         ↓
    (qualquer um acessa)
         ↓
Seu jogo no Play Store
```

---

## ❓ Perguntas Frequentes

**P: Quanto custa?**
R: Groq tem plano gratuito! Você pode usar sem pagar (com limites).

**P: Posso usar em produção?**
R: Sim! O projeto está pronto para produção.

**P: Preciso de GPUs caras?**
R: Não! Groq faz o processamento pesado. Você só precisa de internet.

**P: Quanto tempo leva para aprender tudo?**
R: Com essa documentação, umas 2-3 horas para entender o básico.

**P: Posso modificar?**
R: Sim! Todo o código está disponível para modificar.

**P: Posso usar meus próprios modelos de IA?**
R: Sim! O projeto é flexível para isso.

---

## 📖 Como Ler a Documentação Completa

Se você quer entender TUDO (não só o básico):

1. **Comece aqui** ← (Você está aqui!)
2. **Leia `STRUCTURE.md`** - Arquitetura detalhada
3. **Leia `SUMARIO_FINAL.md`** - Resumo do que foi feito
4. **Explore `/docs/`** - Documentação técnica específica

---

## ✅ Resumo ULTRA Rápido

```
O quê?        Sistema de IA que responde perguntas
Como?         Procura em seus documentos + usa IA
Por quê?      Serve para jogos, apps, suporte, etc
Quando?       2-3 segundos por pergunta
Quanto?       Grátis (com limites)
Onde?         Na sua máquina ou em um servidor
Quem faz?     Você e a IA juntos
```

---

**Pronto? Vá para o Passo 1 em "Começar (5 Passos Simples)"!** 🚀

Qualquer dúvida, é só me chamar! 😊
