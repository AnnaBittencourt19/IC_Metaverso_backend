#Esse vai ser o arquivo principal do servidor FastAPI, vai ser feito a insancia do fastapi, adicionado o middleware de CORS , registro de rotas da API, importacao de outras funcinalidades (o mqtt, websockets, IA, etc)
#Apenas recebe pedidos e retorna

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "*" #apenas para testes, remover em producao
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],   
    allow_headers=["*"],    
)