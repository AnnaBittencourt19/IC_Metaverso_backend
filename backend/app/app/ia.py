#aqui vai ser construida a IA, a logica da ia 
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA