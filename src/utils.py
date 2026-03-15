from functools import lru_cache
from langchain_pinecone import PineconeVectorStore
# Tambahkan ini agar VPS bisa menemukan folder src kamu
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.config import PINECONE_INDEX_NAME
from src.embedding import JinaEmbedding


@lru_cache(maxsize=1)
def load_vectorstore(index_name: str = PINECONE_INDEX_NAME, dimensions: int = 512):
    # Inisialisasi sekali, dipakai ulang untuk request berikutnya
    embedding_function = JinaEmbedding(dimensions=dimensions)
    return PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_function,
    )


def similarity_search(query, vectorstore, k=3):
    results = vectorstore.similarity_search(query, k=k)
    for r in results:
        print(r.page_content)
        print("Metadata:", r.metadata)
        print("-----")
    return results


def build_context(docs):
    context = ""
    for i, doc in enumerate(docs):
        context += f"{i+1}. {doc.page_content}\n"
        if doc.metadata:
            context += f" Lokasi: {doc.metadata.get('lokasi', '-')}\n"

    return context


def build_prompt(context, query):
    return f"""
Anda adalah asisten rekomendasi kuliner berbasis data Instagram.

Gunakan informasi berikut untuk menjawab pertanyaan pengguna.
Jika data tidak ditemukan, katakan dengan jujur.

Data:
{context}

Pertanyaan:
{query}

Jawaban:
"""