1. Criação do arquivo main.py e adição da configuração do CORS: (Arquivo onde o servidor HTTP será configurado)
```python
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
```
	-Esse código garante que o Unity e outras aplicações possam se conectar à API sem bloqueios, mesmo rodando em portas e domínios diferentes
	