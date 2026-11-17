import logging
import sys

from config.config import DATA_DIR, PINECONE_INDEX_NAME
from src.build_documents import create_documents
from src.embedding import JinaEmbedding
from src.load_data import load_csv
from src.vector_store import build_vector_store

logger = logging.getLogger(__name__)


def main():
    try:
        print("--- Loading and Validating Data ---")
        df = load_csv(DATA_DIR)
        docs, ids = create_documents(df)
        print(f"Validated {len(docs)} documents with unique deterministic IDs")

        print("--- Initializing Jina Embeddings ---")
        embedding_function = JinaEmbedding()
        print(f"--- Uploading to Pinecone Index: {PINECONE_INDEX_NAME} ---")
        build_vector_store(
            documents=docs, ids=ids, index_name=PINECONE_INDEX_NAME,
            embedding_function=embedding_function,
        )
    except (ValueError, FileNotFoundError) as error:
        print(f"Data atau konfigurasi ingest tidak valid: {error}", file=sys.stderr)
        return 1
    except Exception:
        logger.exception("Ingest gagal; sebagian batch mungkin sudah tertulis di Pinecone.")
        return 1
    print(f"Selesai! {len(ids)} dokumen berhasil di-ingest ke Pinecone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
