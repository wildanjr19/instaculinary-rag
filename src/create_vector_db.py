import os
from dotenv import load_dotenv
# Tambahkan ini agar VPS bisa menemukan folder src kamu
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.load_data import load_csv
from src.build_documents import create_documents
from src.embedding import JinaEmbedding  
from src.vector_store import build_vector_store
from config.config import DATA_DIR, PINECONE_INDEX_NAME

load_dotenv()

def main():
    # 1. Load data kuliner
    print("--- Loading Data ---")
    df = load_csv(DATA_DIR)
    docs = create_documents(df)
    
    # 2. Inisialisasi Jina Embedding
    print("--- Initializing Jina Embeddings ---")
    embedding_function = JinaEmbedding(dimensions=512) 
    
    # 3. Kirim ke Pinecone 
    print(f"--- Uploading to Pinecone Index: {PINECONE_INDEX_NAME} ---")
    try:
        vector_db = build_vector_store(
            documents=docs,
            index_name=PINECONE_INDEX_NAME,
            embedding_function=embedding_function
        )
        print(f"Selesai! Data berhasil di-ingest ke Pinecone.")
        
    except Exception as e:
        print(f"Terjadi kesalahan saat upload: {e}")

if __name__ == "__main__":
    main()