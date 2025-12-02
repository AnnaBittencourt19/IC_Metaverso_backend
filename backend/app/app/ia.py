#aqui vai ser construida a IA, a logica da ia 
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
query = "Exemplo"
embedding = model.encode(query)
print(embedding.shape)

