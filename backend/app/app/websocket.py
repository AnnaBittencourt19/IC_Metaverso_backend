#aqui tambem usara fastAPI, sera o modulo que fara a comunicacao via websocket entre o servidor e o cliente (frontend), enviando e recebendo mensagens em tempo real
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

