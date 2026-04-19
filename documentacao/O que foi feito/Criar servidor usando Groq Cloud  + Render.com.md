
- Google Drive (PDFs) → Render.com (FastAPI + ChromaDB + Embeddings) → Groq Cloud (Llama 3.1-8B)
- Baixei o chroma bd (pasta dos embeddings) em zip (vou subir no render disk isso)
- Precisa de uma estrutura na pasta:
- metaverso/
	- Requeriments.txt (bibliotecas que seram baixadas)
	- render.yaml (configurações do render/deploy)
	- .env
	- app/
		- main.py (vai ser o servidor)
		- rag.py (RAG/IA)
		- config.py (variaveis ambiente)
		- ingest.py (pdfs)
![[Captura de Tela 2026-04-07 às 22.36.23.png]]
### Visão geral
- Transformar o notebook (colab)(.ipnyb) em uma API backend production ready
- Pastas: 
	- app/ 
	- docs/
	- config/
	- chroma_db_export/
	- Data/
	- tests/
	- arquivos de configuração
### app/
- Possui 5 endpoints (GET/ , GET /api/v1/health, GET /api/v1/info, POST /api/v1/ask e POST /api/v1/ask-audio)
	- GET / Página inicial 
	- GET /api/v1/health verifica a saude
	- GET /api/v1/info Informações do sistema
	- POST /api/v1/ask Processa perguntas de texto
	- POST /api/v1/ask-audio pegunta por audio

- O que é API production ready?
	- API permite comunicação entre sistemas 
	- Production Ready Pronto para produção