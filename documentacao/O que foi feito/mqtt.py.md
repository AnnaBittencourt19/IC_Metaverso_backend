1. Instalando o paho-mqtt via poetry: 
```shell
annabittencourt@MacBook-Air-de-Anna app % poetry add --group mqtt paho-mqtt    

Using version **^2.1.0** for paho-mqtt

  

Updating dependencies

Resolving dependencies... (0.1s)

  

**Package operations**: 1 install, 0 updates, 0 removals

  

  **-** Installing paho-mqtt (2.1.0)

  

Writing lock file
```

2. Importações básicas:
```python
from fastapi import FastAPI, WebSocket from fastapi.responses import HTMLResponse app = FastAPI() 
```
