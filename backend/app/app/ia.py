import os
import glob
import fitz  
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

PDF_DIR = '/Users/annabittencourt/projetos/IC_METAVERSO/backend/app/Data'
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CROSS_ENCODER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"Usando dispositivo: {device}")

def clean_text_content(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    text = text.strip()
    
    lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
    return '\n'.join(lines)

def load_pdfs(directory):
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
            
    logging.info(f"Total de páginas extraídas: {len(documents)}")
    return documents

def chunk_documents(documents):
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
    
    logging.info(f"Total de chunks gerados: {len(filtered_chunks)}")
    return filtered_chunks

def setup_vectorstore(chunks):
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
    
    logging.info("Vector store configurado com sucesso")
    return base_retriever, embeddings

class ReRankingRetriever:
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

def create_semantic_answer(context, question, embeddings):
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
    
    if relevant_sentences:
        answer = '. '.join(relevant_sentences)
        if not answer.endswith('.'):
            answer += '.'
        return answer
    else:
        top_sentences = [sent for sent, score in sentence_scores[:2]]
        answer = '. '.join(top_sentences)
        if not answer.endswith('.'):
            answer += '.'
        return answer

def query_rag(question, retriever, embeddings):
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
        context_parts.append(text[:400])
        sources.append(doc.metadata)
    
    context_text = "\n\n".join(context_parts)
    
    answer = create_semantic_answer(context_text, question, embeddings)
    
    final_answer = post_process_answer(answer, question)
    
    return {
        "answer": final_answer,
        "sources": sources,
        "context_length": len(context_text)
    }

def post_process_answer(answer, question):
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
    
    if not unique_sentences:
        return answer
    
    final_sentences = unique_sentences[:2]
    clean_answer = '. '.join(final_sentences)
    
    if not clean_answer.endswith('.'):
        clean_answer += '.'
    
    return clean_answer if len(clean_answer) > 30 else answer

if __name__ == "__main__":
    if not os.path.exists(PDF_DIR):
        print(f"ERRO: Diretório {PDF_DIR} não encontrado.")
        exit()

    print("--- Iniciando Pipeline RAG ---")
    
    docs = load_pdfs(PDF_DIR)
    if not docs:
        print("Nenhum PDF encontrado.")
        exit()
        
    chunks = chunk_documents(docs)
    
    base_retriever, embeddings = setup_vectorstore(chunks)
    
    logging.info("Carregando cross-encoder para re-ranking...")
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    
    retriever = ReRankingRetriever(base_retriever, cross_encoder, top_k=3)
    
    print("\n--- Sistema Pronto. Digite 'sair' para encerrar. ---")
    while True:
        user_q = input("\nPergunta: ")
        if user_q.lower() in ['sair', 'exit']:
            break
            
        result = query_rag(user_q, retriever, embeddings)
        
        print(f"\n>> Resposta: {result['answer']}")
        print("\n>> Fontes:")
        for source in result['sources']:
            print(f" - {source['source']} (Pág {source['page']})")