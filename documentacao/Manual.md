##### Arquitetura de microsserviços:
-  O que é feito no Unity é cliente (não acessa diretamente banco de dados ou coisas externas) ele recebe e envia dados de um servidor (por Web Request (HTTP))
- Front-end (O metaverso): Unity(C#), interface em si do metaverso, onde o usuario vê e interage 
- Back-end: Python será a lógica em si, dados, treinamento, funções, etc
- Servidor: Django ou FastAP, vai fazer a ligação entre os pedidos do usuario, passar pro backend e devolver a resposta pro front
##### Porque ter um servidor
- Envio e recebimento de dados
- Para que o metaverso receba uma informação é necessário fazer um GET
- Para o metaverso enviar uma informação para o servidor usasse POST
- Guardar dados e armazenar logs 
- O servidor não faz o trabalho ele só transporta e organiza os pedidos
##### Escolha do framework
- A escolha de um framework é essencial para o desenvolvimento da IA e do gêmeo digital, essa escolha influencia no desempenho, na escalabilidade e no processo de desenvolvimento do projeto

	- Flask: Mais básico de todos, sincrono, fácil de entender, requer bibliotecas adicionais (iniciante)
	- FastAPI: Intermediario, foi projetado para ser rápido e fácil de usar, não tem tantos recursos quanto o django (intermediário, ideal para o projeto devido a sua rapidez)
	- Django: Avançado porém pode ser mais complexo de se usar e lento, usado para aplicações mais complexas (completo e seguro porém pesado)
	
[Sobre qual framework usar](https://medium.com/@cubode/whats-the-best-backend-framework-for-ai-development-in-2024-django-fastapi-or-flask-d52c165ea20c)

- O que vai conectar o Front-end (o metaverso visual) com o backend (a parte que "pensa") vai ser o Web Request, o script C# no Unity vai fazer chamadas (UnityWebRequest) para o servidor Python criado
- No backend fica as funções a lógica em si
##### Requisição HTTP
- GET: Front end recebe uma informação
- POST: Front end manda um comando
- PUT: Atualizar alguma coisa
- DELETE: Apagar algo
- O front end só pede e manda informações
##### O que é uma API?
- Uma API é o que faz o front end conversar com o backend
- Exemplos de APIs famosas: 
	- API do Google Maps: Para coordenadas e mapas
	- API do PayPal: Para processar pagamentos e transferências online
	- API do google drive: Acessar os recurso do google drive
	- Firebase: Autenticação, banco de dados e hospedagem
	- Watson: Oferece uma serie série de serviços de inteligencia artificial, incluindo processamento de linguagem natural, reconhecimento de fala, análise de sentimentos e outras ferramentas avançadas de IA e Machine Learning (ESTUDAR SOBRE INTERESSANTE)
##### Exemplo usando o projeto de base:

1. Frontend 
	- O usuário vai clicar em um botão (por exemplo para acender a luz)
	- Interface
	- O Unity/C# manda um pedido HTTP:
```C#
POST http://meuservidor.com/lab/ligar_luz
```
		- No Unity só mostra e envia comandos ele não sabe executa-los

2. Servidor (FastAPI ou Django)
	- Recebe o pedido HTTP (/lab/ligar_luz)
	- Entende o que foi pedido
	- Manda o pedido para o backend chamando a função Python correspondente 
	- Transporta pedidos
	- "Meio de transporte"

3. Backend (Python)
	- Executa a função que liga a luz (executa a ação e devolve uma resposta em JSON)
	- Lógica e conteúdo
	- Retorna uma resposta JSON:
```JSON
{"status": "Luz ligada com sucesso!"}
```

4. Servidor manda a resposta para o Unity
	- O frontend recebe o JSON
	- Atualiza a cena de acordo com o que recebeu
##### O que é uma requisição HTTP
- O Unity (frontend) e o FastAPI/Django conversam por meio de mensagens HTTP
- Tem duas partes:
	- Requisição: O pedido do frontend
	- Resposta: O que o servidor responde
	- ##### Como é feita uma requisição:
		- URL: Endereço
		- Método HTTP: Ação (get, post, put, delete)
		- Cabeçalhos: Informações adicionais 
		- Corpo: O que será enviado (JSON)
		- Como é o formato de um JSON:
			- "chave": valor (exemplo: { "luz": "ligada"})
- **Resumindo:** HTTP é uma especie de idioma que o Unity e o Python vão usar para se comunicar, tem a requisição (o pedido feito pelo usuario usando um método como GET) e a resposta ( o que o servidor recebeu do backend e vai mandar para o front)
##### Vantagens Web socket
- Cliente ou servidor podem enviar dados 
- Uma conexão fica aberta 
- É ideal para o uso em coisas que envolvem sensores em tempo real

#### Decisões até aqui (mutáveis):
######  - Fazer o backend e conexão:
- Python, FastAPI, WebSocket(gêmeo digital) e HTTP (LLM)
- Código de backend usando Websocket e FastAPI (gêmeos digitais vai usar websocket):
```python
import asyncio
from fastapi import FastAPI, WebSocket
import paho.mqtt.client as mqtt

app = FastAPI()
websocket_clients = []
global_loop = None

@app.on_event("startup")
async def startup_event():
    global global_loop
    global_loop = asyncio.get_running_loop()

def on_mqtt_message(client, userdata, msg):
    data = msg.payload.decode()
    for ws in websocket_clients.copy():
        asyncio.run_coroutine_threadsafe(ws.send_text(data), global_loop)

MQTT_BROKER = "localhost"
MQTT_TOPIC = "parking/sensor"

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_mqtt_message
mqtt_client.username_pw_set("admin", "admin")
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.loop_start()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        websocket_clients.remove(websocket)

@app.get("/")
async def root():
    return {"message": "Welcome to the Digital Twin API. Use /ws for WebSocket connection."}
```
- Repositório github gêmeo digital com FastAPI e websocket: https://github.com/TarunAiyappa/smart-parking-digital-twin/tree/main
- Protocolo MQTT: Para a comunicação do servidor FastAPI e a lâmpada física
		Unity <-> FastAPI <-> lâmpada
	- O MQTT é melhor que o HTTP nesse caso, pois o MQTT usa um intermediário (Broker) para que a lâmpada e o servidor conversem gastando menos dados (Broker é como se fosse um atalho)
###### - Fazer o LLM:
- RAG (para alimentar com os PDFs sobre o Inatel e os projetos do XGmobile)
- Motivos da escolha do RAG: 
	- Ao longo do tempo coisas sobre o Inatel, projetos e até mesmo locais podem mudar com isso o RAG é mais fácil de organizar e atualizar os dados (colocando novos pdfs), o uso de fine-tuning seria mais complexo pois teria que re-treinar em caso de futuras mudanças 
	- Um RAG é basicamente aprimorar um LLM com dados externos (no caso PDFs)
	- A resposta é embasada nos documentos 
- LangChain: Framework para simplificar a criação do pipeline de RAG
	- Possui opções de carregadores de PDFs (PyPDFLoader, Pymupdf)
	- Possui ferramentas para fragmentar documentos em chuckings (RecursiveCharacterTextSplitter)
	- Modelos de Embeddings (converter os chuckings em embeddings(vetores numéricos))
	- Vector Stores: Armazenar e consultar embeddings (FAISS)
	- Modelos de prompt
- Usar um modelo de embedding multilingue (artigos em inglês, possíveis informações sobre o xgmobile e o inatel em português). Essa situação de multilingue trás um desafio, então usar uma biblioteca multilingue ou traduzir os artigos para português (o que eu acredito que embora mais arcaico e não apropriado pois a tradução pode fazer termos técnicos se perderem)
- Pydantic: Padronizar formatos de JSON (evitar erro de formatos de dados)

##### EXTRA: 

- PostgreSQL: Para armazenar logs de eventos e histórico de estados (igual em digital vai lembrar se a luz estava ligada ou desligada, aí se mandar ligar a luz tem que estar desligada pra ela ligar e se tiver ligada já continua ligada)
	- Também pode armazenar dados para uma criação de dashboards
	- Também ajuda a armazenar estados em caso do WebSocket e o MQTT derem problema
	
- SQLModel: É uma combinação de SQLAlchemy + Pydantic

- CORS Middleware: Resolve o problema de origem cruzada (dominio diferente/porta). O Unity e o FastAPI possuem origens diferentes e o sistema bloqueia essa comunicação, como implementar:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importe o middleware

app = FastAPI()

# Esta é a lista de origens que têm permissão para fazer requisições à sua API.
origins = [
    "http://localhost",
    "http://localhost:8080",
    # Adicione aqui a URL/IP exata de onde seu Unity estará rodando.
    # Se você não sabe, usar "*" (todos) é ok para desenvolvimento,
    # mas inseguro para produção.
    # Exemplo: "http://192.168.1.10:5500"
    "*" # Apenas para desenvolvimento
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Quais origens podem se conectar
    allow_credentials=True, # Permite cookies (importante para autenticação)
    allow_methods=["*"],    # Quais métodos HTTP são permitidos (GET, POST, etc.)
    allow_headers=["*"],    # Quais cabeçalhos HTTP são permitidos (ex: "Authorization")
)
```

##### Conteinerização
- Docker
- Pega tudo do aplicativo e guardar para funcionar em outros lugares 

##### Implantação/Deployment
- Uvicorn + Gunicorn 
- Fazer com que o servidor aceite vários clientes sem travar
##### Lacunas 
- Colocar timeouts (tempo limite)
- Usar os códigos HTTP certos para que os erros sejam especificados, colocar JSONs justificando erros (ex: {"erro": "O dispositivo não respondeu"})
- Adicionar Try/Except para ter mais controle sob os erros

![[UML.svg]]

- OBS: Banco de dados e devops são extras (depois de tudo ficar pronto)