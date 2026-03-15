from langchain_pinecone import PineconeVectorStore  

# Tambahkan ini agar VPS bisa menemukan folder src kamu
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.embedding import JinaEmbedding  

def build_vector_store(documents, index_name, embedding_function):
    vector_db = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embedding_function,
        index_name=index_name,
    )
    return vector_db