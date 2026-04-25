"""Script de ingestão para o build do Docker."""
import os
import re
import logging
import chromadb
from app.rag import load_pdfs_improved, chunk_documents, SentenceTransformerEmbeddings
from app.config import PDF_DIR, CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"PDF_DIR: {PDF_DIR}")
logger.info(f"CHROMA_PERSIST_DIR: {CHROMA_PERSIST_DIR}")

documents = load_pdfs_improved(PDF_DIR)
if not documents:
    raise RuntimeError(f"Nenhum PDF encontrado em {PDF_DIR}")

chunks = chunk_documents(documents)
if not chunks:
    raise RuntimeError("Nenhum chunk criado")

for c in chunks:
    c.page_content = 'passage: ' + re.sub(r'^(passage: )+', '', c.page_content)

logger.info(f"Total de chunks: {len(chunks)}")

embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

try:
    client.delete_collection("6g_docs")
except Exception:
    pass

collection = client.create_collection("6g_docs")

batch_size = 100
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i + batch_size]
    texts = [c.page_content for c in batch]
    metadatas = [c.metadata for c in batch]
    ids = [f"doc_{i + j}" for j in range(len(batch))]
    embeds = embeddings.embed_documents(texts)
    collection.add(embeddings=embeds, documents=texts, metadatas=metadatas, ids=ids)
    logger.info(f"Inseridos {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")

logger.info(f"Ingestão concluída: {collection.count()} documentos no banco")
