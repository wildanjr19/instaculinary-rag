from src.utils import load_vectorstore


def search_documents(query, k=5):
    vectorstore = load_vectorstore()
    docs = vectorstore.similarity_search(query, k=k)
    return docs
