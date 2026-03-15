"""Path"""
import os

# Gunakan path absolut untuk menghindari error relatif
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# LOCAL DATA DIR
DATA_DIR = os.path.join(ROOT_DIR, "data", "04_knowledge_base", "knowledge_base_v1.csv")

# LOCAL EMBEDDING MODEL
EMBEDDING_MODEL = os.path.join(ROOT_DIR, "models", "embedding", "multilingual-e5-small")

# LOCAL CHROMA DB
# CHROMA_DIR = os.path.join(ROOT_DIR, "vector_db", "chroma_db")

# PINECONE CONFIG
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "culinary-rag-data"
PINECONE_ENVIRONMENT = "us-east-1"