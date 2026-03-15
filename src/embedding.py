import os
import time
import random
import requests
from typing import List
from langchain_core.embeddings import Embeddings

class JinaEmbedding(Embeddings):
    def __init__(self, api_key=None, dimensions=512, batch_size=32, max_retries=5):
        self.api_key = api_key or os.getenv("JINA_AI_API_KEY")
        self.url = "https://api.jina.ai/v1/embeddings"
        self.dimensions = dimensions
        self.model = "jina-embeddings-v3"
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.timeout = (10, 60)  # connect, read

        if not self.api_key:
            raise ValueError("JINA_AI_API_KEY tidak ditemukan di environment variable!")

        self.session = requests.Session()

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _post_embeddings(self, inputs: List[str], task: str) -> List[List[float]]:
        payload = {
            "model": self.model,
            "task": task,
            "dimensions": self.dimensions,
            "input": inputs
        }

        for attempt in range(self.max_retries):
            try:
                resp = self.session.post(
                    self.url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )

                # retryable
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"Retryable status: {resp.status_code}", response=resp)

                resp.raise_for_status()
                data = resp.json().get("data", [])
                if len(data) != len(inputs):
                    raise ValueError(
                        f"Jumlah embedding tidak cocok. input={len(inputs)} output={len(data)}"
                    )

                # Jina biasanya sudah urut, tapi ini lebih aman bila ada field index
                if data and "index" in data[0]:
                    data = sorted(data, key=lambda x: x["index"])

                return [item["embedding"] for item in data]

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Gagal setelah {self.max_retries} percobaan: {e}") from e

                backoff = (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(backoff)

        raise RuntimeError("Unexpected retry loop exit")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        clean_texts = [t for t in texts if isinstance(t, str) and t.strip()]
        all_embeddings: List[List[float]] = []

        for i in range(0, len(clean_texts), self.batch_size):
            batch = clean_texts[i:i + self.batch_size]
            emb = self._post_embeddings(batch, task="retrieval.passage")
            all_embeddings.extend(emb)
            time.sleep(0.2)  # throttle ringan

        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        return self._post_embeddings([text], task="retrieval.query")[0]