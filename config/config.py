"""Konfigurasi bersama untuk backend, CLI, dan ingest data."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
# Environment dari shell/deployment tetap memiliki prioritas atas file .env.
load_dotenv(ROOT_DIR / ".env", override=False)

DATA_DIR = ROOT_DIR / "data" / "04_knowledge_base" / "knowledge_base_v2.csv"
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") or "instaculinary-data"
EMBEDDING_DIMENSIONS = 512


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} belum diisi. Atur di environment atau .env root proyek.")
    return value
