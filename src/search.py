from config.config import PINECONE_INDEX_NAME
# Tambahkan ini agar VPS bisa menemukan folder src kamu
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.utils import load_vectorstore


def search_documents(query, k=5):
    vectorstore = load_vectorstore(index_name=PINECONE_INDEX_NAME, dimensions=512)
    docs = vectorstore.similarity_search(query, k=k)
    return docs