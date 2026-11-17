from functools import lru_cache
from langchain_pinecone import PineconeVectorStore
from config.config import EMBEDDING_DIMENSIONS, PINECONE_INDEX_NAME, get_required_env
from src.embedding import JinaEmbedding
from src.normalization import (
    MISSING_INFO, normalize_account, normalize_document_text, normalize_instagram_url, normalize_text,
)


@lru_cache(maxsize=1)
def load_vectorstore(index_name: str = PINECONE_INDEX_NAME, dimensions: int = EMBEDDING_DIMENSIONS):
    # Inisialisasi sekali, dipakai ulang untuk request berikutnya
    embedding_function = JinaEmbedding(dimensions=dimensions)
    return PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_function,
        pinecone_api_key=get_required_env("PINECONE_API_KEY"),
    )


def similarity_search(query, vectorstore, k=3):
    results = vectorstore.similarity_search(query, k=k)
    for r in results:
        print(r.page_content)
        print("Metadata:", r.metadata)
        print("-----")
    return results


def build_context(docs):
    """Membangun konteks terstruktur dari dokumen hasil retrieval.
    Setiap field diberi label yang jelas agar LLM mudah mem-parsing."""
    context = ""
    for i, doc in enumerate(docs):
        meta = doc.metadata if doc.metadata else {}
        source = normalize_account(meta.get("sumber"))
        source_url = normalize_instagram_url(meta.get("url"), source)
        context += (
            f"--- Dokumen {i+1} ---\n"
            f"Nama Tempat: {normalize_text(meta.get('nama'), MISSING_INFO)}\n"
            f"Kategori: {normalize_text(meta.get('kategori'), MISSING_INFO)}\n"
            f"Deskripsi: {normalize_text(meta.get('deskripsi'), MISSING_INFO)}\n"
            f"Opini Food Vlogger: {normalize_text(meta.get('opini'), MISSING_INFO)}\n"
            f"Area: {normalize_text(meta.get('daerah'), MISSING_INFO)}\n"
            f"Sumber Akun: {source or MISSING_INFO}\n"
            f"URL Postingan: {source_url or MISSING_INFO}\n"
            f"\nDetail Lengkap:\n{normalize_document_text(doc.page_content, source)}\n\n"
        )
    return context


def build_prompt(context, query):
    """Prompt JSON-first untuk RAG Kuliner Jogja & Solo.
    LLM dipaksa hanya mengembalikan JSON valid tanpa teks tambahan."""
    return f"""Kamu adalah asisten rekomendasi kuliner untuk area Jogja dan Solo (Jawa Tengah & DIY).
Kamu hanya bekerja berdasarkan data Instagram food vlogger yang diberikan di bawah.

TUGAS:
Berdasarkan KONTEKS di bawah, rekomendasikan tempat makan yang PALING RELEVAN dengan pertanyaan pengguna.
Pilih dan urutkan dari yang paling cocok (maksimal 5 tempat).

ATURAN OUTPUT (WAJIB DIPATUHI):
1. Jawab HANYA dalam format JSON valid. JANGAN tambahkan teks, penjelasan, markdown, atau kode blok (```) di luar JSON.
2. Jika tidak ada data relevan, tetap kembalikan JSON dengan array "results" kosong dan "query_summary" yang menjelaskan bahwa tidak ditemukan.
3. Gunakan deskripsi 2-3 kalimat yang informatif dan menggugah selera.
4. "hours" diisi dengan format "HH:MM - HH:MM" jika jam buka dan tutup tersedia. Jika tidak, isi "Informasi tidak tersedia".
5. "price" diisi dengan rentang harga atau indikasi (contoh: "Rp 15.000 - Rp 35.000", "Mulai Rp 10.000", atau "Informasi tidak tersedia").
6. "source_url" diisi dengan URL postingan asli dari field "URL Postingan" yang ada di konteks. Jika URL tidak tersedia, fallback ke format https://instagram.com/[nama_akun] (tanpa @).

Format JSON output:
{{
  "query_summary": "Ringkasan 1 kalimat tentang apa yang dicari pengguna",
  "results": [
    {{
      "rank": 1,
      "name": "Nama Tempat Makan",
      "address": "Alamat lengkap",
      "hours": "07:00 - 21:00",
      "price": "Rp 15.000 - Rp 35.000",
      "categories": ["Kategori1", "Kategori2"],
      "description": "Deskripsi 2-3 kalimat. Ceritakan suasana, menu andalan, dan keunikan tempat.",
      "source": "@namaakun",
      "source_url": "https://instagram.com/namaakun"
    }}
  ]
}}

KONTEKS (Data Instagram Food Vlogger):
{context}

PERTANYAAN PENGGUNA:
{query}

JSON:"""
