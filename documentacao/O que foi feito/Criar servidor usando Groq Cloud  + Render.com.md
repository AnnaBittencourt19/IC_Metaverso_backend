
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