"""
Script untuk embedding menggunakan SentenceTransformer dengan model embedding local.
"""

from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbedding:
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True).tolist()
    
    def embed_query(self, text):
        return self.model.encode(text).tolist()