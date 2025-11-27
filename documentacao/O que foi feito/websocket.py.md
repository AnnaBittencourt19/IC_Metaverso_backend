1. Não precisa instalar o websocket ele já vem incluso em poetry add 'fastapi[standard]'
2. Adição de imports básicos:
```python
#aqui tambem usara fastAPI, sera o modulo que fara a comunicacao via websocket entre o servidor e o cliente (frontend), enviando e recebendo mensagens em tempo real

from fastapi import FastAPI, WebSocket

from fastapi.responses import HTMLResponse

app = FastAPI()
```
