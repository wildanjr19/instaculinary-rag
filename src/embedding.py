import math
import random
import time

import requests
from langchain_core.embeddings import Embeddings

from config.config import EMBEDDING_DIMENSIONS, get_required_env

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class JinaEmbedding(Embeddings):
    def __init__(self, api_key=None, dimensions=EMBEDDING_DIMENSIONS, batch_size=32, max_retries=3):
        if any(type(value) is not int or value < 1 for value in (dimensions, batch_size, max_retries)):
            raise ValueError("dimensions, batch_size, dan max_retries harus integer positif.")
        self.api_key = api_key or get_required_env("JINA_AI_API_KEY")
        self.url = "https://api.jina.ai/v1/embeddings"
        self.dimensions = dimensions
        self.model = "jina-embeddings-v3"
        self.batch_size = batch_size
        self.max_retries = max_retries  # Jumlah percobaan total, termasuk request pertama.
        self.timeout = (5, 15)  # Batas connect dan read per percobaan, dalam detik.

    @staticmethod
    def _validate_texts(texts):
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("Setiap teks embedding harus berupa string yang tidak kosong.")

    def _parse_embeddings(self, payload, count):
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list) or len(data) != count or any(not isinstance(item, dict) for item in data):
            raise ValueError("Jumlah atau format embedding tidak sesuai input.")
        if any("index" in item for item in data):
            indices = [item.get("index") for item in data]
            if any(type(index) is not int for index in indices) or sorted(indices) != list(range(count)):
                raise ValueError("Index embedding harus unik dan sesuai urutan input.")
            data = sorted(data, key=lambda item: item["index"])
        vectors = [item.get("embedding") for item in data]
        for vector in vectors:
            if (
                not isinstance(vector, list) or len(vector) != self.dimensions
                or any(type(value) not in (int, float) or not math.isfinite(value) for value in vector)
            ):
                raise ValueError("Vektor embedding harus numerik, finite, dan sesuai dimensi index.")
        return vectors

    def _post_embeddings(self, inputs: list[str], task: str) -> list[list[float]]:
        payload = {"model": self.model, "task": task, "dimensions": self.dimensions, "input": inputs}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(self.max_retries):
            try:
                # Session per request menghindari state/cookie bersama antarthread.
                # Redirect dimatikan agar kredensial tidak mengikuti destinasi lain.
                with requests.post(
                    self.url, json=payload, headers=headers,
                    timeout=self.timeout, allow_redirects=False,
                ) as response:
                    if 300 <= response.status_code < 400:
                        raise requests.HTTPError("Redirect layanan embedding ditolak.", response=response)
                    response.raise_for_status()
                    return self._parse_embeddings(response.json(), len(inputs))
            except requests.exceptions.SSLError:
                raise
            except requests.HTTPError as error:
                status = error.response.status_code if error.response is not None else None
                if status not in _RETRYABLE_STATUS or attempt == self.max_retries - 1:
                    raise
            except (requests.Timeout, requests.ConnectionError):
                if attempt == self.max_retries - 1:
                    raise
            time.sleep((2 ** attempt) + random.uniform(0, 0.5))

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Validasi seluruh input sebelum batch pertama; jangan menggeser pasangan dokumen/ID.
        self._validate_texts(texts)
        vectors = []
        for offset in range(0, len(texts), self.batch_size):
            batch = texts[offset:offset + self.batch_size]
            vectors.extend(self._post_embeddings(batch, task="retrieval.passage"))
            if offset + self.batch_size < len(texts):
                time.sleep(0.2)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        self._validate_texts([text])
        return self._post_embeddings([text], task="retrieval.query")[0]
