from langchain_pinecone import PineconeVectorStore

from config.config import get_required_env

def build_vector_store(documents, ids, index_name, embedding_function):
    if not documents or len(documents) != len(ids):
        raise ValueError("Jumlah dokumen dan ID harus sama dan tidak kosong.")
    if any(not isinstance(doc_id, str) or not doc_id.strip() for doc_id in ids) or len(set(ids)) != len(ids):
        raise ValueError("ID dokumen harus berupa string unik dan tidak kosong.")
    if any(not doc.page_content.strip() for doc in documents):
        raise ValueError("Konten dokumen tidak boleh kosong.")
    vector_db = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embedding_function,
        index_name=index_name,
        ids=ids,  # ID deterministik → bisa upsert di masa depan
        pinecone_api_key=get_required_env("PINECONE_API_KEY"),
    )
    return vector_db
