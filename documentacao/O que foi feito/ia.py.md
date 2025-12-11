1. Instalação das dependências principais:
```shell
annabittencourt@MacBook-Air-de-Anna app % poetry add sentence-transformers
annabittencourt@MacBook-Air-de-Anna app % poetry add scikit-learn
annabittencourt@MacBook-Air-de-Anna app % poetry add PyMuPDF
annabittencourt@MacBook-Air-de-Anna app % poetry add langchain-chroma
annabittencourt@MacBook-Air-de-Anna app % poetry add langchain-text-splitters
annabittencourt@MacBook-Air-de-Anna app % poetry add langchain-community
annabittencourt@MacBook-Air-de-Anna app % poetry add chromadb
```
	- Por que essas libs? Cada uma tem uma função específica no pipeline RAG que criei

2. Imports que uso (tive que atualizar por causa das versões novas do LangChain):
```python
import os
import glob
import fitz  # PyMuPDF para ler PDFs
import torch
import numpy as np
import logging
import re
from sentence_transformers import CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings
from sklearn.metrics.pairwise import cosine_similarity
```
	- Problema: LangChain mudou os imports nas versões novas, tive que ajustar tudo
	- Se der erro de ModuleNotFoundError, é por causa disso

3. Configurações básicas:
```python
PDF_DIR = '/Users/annabittencourt/projetos/IC_METAVERSO/backend/app/Data'
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CROSS_ENCODER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```
	- PDF_DIR: pasta com os 15 PDFs sobre 6G
	- EMBEDDING_MODEL: modelo multilíngue que funciona bem com português
	- CROSS_ENCODER: para re-ranking e melhorar precisão
	- device: usa GPU se tiver, senão CPU mesmo

4. Função para ler PDFs:
```python
def load_pdfs(directory):
    """Lê PDFs recursivamente e extrai texto com metadados."""
    logging.info(f"Buscando PDFs em: {directory}")
    documents = []
    
    files = glob.glob(os.path.join(directory, '**/*.pdf'), recursive=True)
    
    for filepath in files:
        try:
            doc = fitz.open(filepath)
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    clean_text = clean_text_content(text)
                    if clean_text:
                        documents.append({
                            "text": clean_text,
                            "metadata": {
                                "source": os.path.basename(filepath),
                                "page": page_num + 1,
                                "path": filepath
                            }
                        })
            doc.close()
        except Exception as e:
            logging.error(f"Erro ao ler {filepath}: {e}")
```
	- Resultado real: 214 páginas extraídas de 15 arquivos
	- Cada página vira um documento com metadados (nome do arquivo, número da página, caminho completo)
	- Usa PyMuPDF porque é mais confiável que outras libs para extrair texto

5. Limpeza do texto extraído:
```python
def clean_text_content(text):
    """Limpa e normaliza o conteúdo do texto."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    text = text.strip()
    
    lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
    return '\n'.join(lines)
```
	- PDFs são bagunçados: espaços duplos, caracteres estranhos, quebras de linha malucas
	- Remove caracteres especiais que atrapalham o processamento
	- Elimina linhas muito curtas (< 10 caracteres) que geralmente são lixo
	- Normaliza espaços para ficar tudo padronizado

6. Divisão em chunks inteligente:
```python
def chunk_documents(documents):
    """Usa RecursiveCharacterTextSplitter otimizado."""
    docs = []
    for doc in documents:
        docs.append(Document(
            page_content=doc['text'],
            metadata=doc['metadata']
        ))
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    
    filtered_chunks = [chunk for chunk in chunks if len(chunk.page_content.strip()) > 30]
```
	- chunk_size=300: testei 512, 256, 400... 300 deu os melhores resultados
	- chunk_overlap=50: sobreposição para não cortar informações importantes no meio
	- separators: tenta quebrar por parágrafo primeiro, depois frase, depois vírgula...
	- Filtra chunks muito pequenos (< 30 caracteres)
	- Resultado final: 1634 chunks úteis de 214 páginas originais

7. Vector store com Chroma:
```python
def setup_vectorstore(chunks):
    """Configura vector store usando Chroma."""
    logging.info("Configurando vector store com HuggingFaceEmbeddings...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': device}
    )
    
    client = chromadb.Client(Settings(
        anonymized_telemetry=False, 
        allow_reset=True, 
        is_persistent=False
    ))
    
    vectorstore = Chroma.from_documents(chunks, embeddings, client=client)
    base_retriever = vectorstore.as_retriever(search_kwargs={'k': 8})
```
	- Transforma cada chunk de texto em um vetor de números (embedding)
	- Embeddings capturam o significado semântico do texto
	- Chroma não-persistente: mais rápido, mas precisa reprocessar toda vez
	- k=8: busca os 8 chunks mais similares inicialmente
	- Por que Chroma? Testei FAISS também, mas Chroma é mais simples de configurar

8. Re-ranking para melhorar precisão:
```python
class ReRankingRetriever:
    """Re-ranking retriever otimizado."""
    def __init__(self, base_retriever, cross_encoder, top_k=3):
        self.base_retriever = base_retriever
        self.cross_encoder = cross_encoder
        self.top_k = top_k

    def get_relevant_documents(self, query: str):
        initial_docs = self.base_retriever.invoke(query)
        
        if len(initial_docs) <= self.top_k:
            return initial_docs
        
        query_doc_pairs = [(query, doc.page_content) for doc in initial_docs]
        scores = self.cross_encoder.predict(query_doc_pairs)
        
        doc_scores = list(zip(initial_docs, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in doc_scores[:self.top_k]]
```
	- Processo em 3 etapas: busca inicial (8 chunks) → re-ranking → seleção final (3 melhores)
	- CrossEncoder analisa se cada chunk realmente responde a pergunta
	- Usa ms-marco-MiniLM-L-6-v2: modelo treinado especificamente para ranking
	- Mudança importante: tive que usar .invoke() ao invés de .get_relevant_documents()

9. Geração de resposta sem keywords:
```python
def create_semantic_answer(context, question, embeddings):
    """Cria resposta baseada em similaridade semântica."""
    sentences = [s.strip() for s in context.replace('\n', ' ').split('.') if s.strip() and len(s.strip()) > 20]
    
    if not sentences:
        return "Não foi possível encontrar informações relevantes no contexto fornecido."
    
    question_embedding = embeddings.embed_query(question)
    sentence_embeddings = embeddings.embed_documents(sentences)
    
    similarities = cosine_similarity([question_embedding], sentence_embeddings)[0]
    
    sentence_scores = list(zip(sentences, similarities))
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    
    relevant_sentences = []
    for sentence, score in sentence_scores:
        if score > 0.15 and len(relevant_sentences) < 3:
            relevant_sentences.append(sentence)
```
	- Calcula similaridade semântica real entre pergunta e cada sentença
	- Threshold 0.15: testei 0.1, 0.2, 0.3... 0.15 captura mais conteúdo sem perder qualidade
	- Máximo 3 sentenças para resposta concisa
	- Funciona para qualquer domínio, não só 6G

10. Pós-processamento da resposta:
```python
def post_process_answer(answer, question):
    """Pós-processa a resposta removendo duplicatas."""
    sentences = [s.strip() for s in answer.split('.') if s.strip()]
    unique_sentences = []
    
    for sentence in sentences:
        if len(sentence) > 15:
            is_duplicate = False
            sentence_words = set(sentence.lower().split())
            
            for existing in unique_sentences:
                existing_words = set(existing.lower().split())
                overlap = len(sentence_words & existing_words)
                if overlap > len(sentence_words) * 0.6:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_sentences.append(sentence)
    
    final_sentences = unique_sentences[:2]
    clean_answer = '. '.join(final_sentences)
```
	- Remove sentenças duplicadas: se 60% das palavras são iguais, considera duplicata
	- Filtra sentenças muito curtas (< 15 caracteres)
	- Limita a 2 sentenças únicas na resposta final
	- Garante que a resposta termine com ponto

11. Pipeline principal:
```python
def query_rag(question, retriever, embeddings):
    """Executa consulta RAG otimizada."""
    logging.info(f"Processando pergunta: {question}")
    
    docs = retriever.get_relevant_documents(question)
    
    if not docs:
        return {
            "answer": "Não foram encontrados documentos relevantes para sua pergunta.",
            "sources": []
        }
    
    context_parts = []
    sources = []
    
    for doc in docs:
        text = doc.page_content.strip()
        text = ' '.join(text.split())
        context_parts.append(text[:500])
        sources.append(doc.metadata)
    
    context_text = "\n\n".join(context_parts)
    
    answer = create_semantic_answer(context_text, question, embeddings)
    final_answer = post_process_answer(answer, question)
    
    return {
        "answer": final_answer,
        "sources": sources,
        "context_length": len(context_text)
    }
```
	- Fluxo completo: pergunta → busca → re-ranking → geração → pós-processamento
	- Limita cada chunk a 500 caracteres para não sobrecarregar
	- Retorna resposta + fontes + tamanho do contexto usado

12. Como rodar o sistema:
```shell
# Ativar ambiente
poetry shell

# Executar
poetry run python ia.py
```

13. Log de execução real:
```
2025-12-11 19:16:30,237 - INFO - Usando dispositivo: cpu
--- Iniciando Pipeline RAG ---
2025-12-11 19:16:30,237 - INFO - Buscando PDFs em: /Users/annabittencourt/projetos/IC_METAVERSO/backend/app/Data
2025-12-11 19:16:30,849 - INFO - Total de páginas extraídas: 214
2025-12-11 19:16:30,860 - INFO - Total de chunks gerados: 1634
2025-12-11 19:16:30,860 - INFO - Configurando vector store com HuggingFaceEmbeddings...
2025-12-11 19:16:43,051 - INFO - Vector store configurado com sucesso
2025-12-11 19:16:43,052 - INFO - Carregando cross-encoder para re-ranking...

--- Sistema Pronto. Digite 'sair' para encerrar. ---
```
	- Tempo de inicialização: ~12 segundos (carregamento dos modelos)
	- Primeira execução sempre demora mais

14. Exemplo de uso real:
```
Pergunta: qual a importancia do 6g?

2025-12-11 19:16:56,096 - INFO - Processando pergunta: qual a importancia do 6g?
Batches: 100%|████████████████████████████████████| 1/1 [00:00<00:00,  1.39it/s]

>> Resposta: Entre os principais destaques esteve a discussão sobre o potencial do 5G-A e as perspectivas para a sexta geração (6G). Expansão do Espectro para as Redes 6G Com o avanço para a rede 6G, espera-se uma ampliação do espectro, incorporando uma variedade de novas faixas.

>> Fontes:
 - xgmobile-comunicacoes-aprimoradas-em-areas-remotas-erac.pdf (Pág 22)
 - 1721934756839xgmobile-faixas-de-frequencias-previstas-para-as-redes-6G.pdf (Pág 5)
 - 1754934759991the-gateway-for-the-future-a-nova-era-das-telecomunicacoes-pos-5g.pdf (Pág 4)
```
	- Tempo de resposta: ~1 segundo
	- Encontrou informações em 3 documentos diferentes
	- Resposta coerente e bem fundamentada

15. Performance medida:
```
Inicialização: ~12 segundos
Processamento por pergunta: ~1 segundo  
Uso de RAM: ~2GB
```


