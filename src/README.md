# Core RAG

Jalur aktif menggunakan Jina AI API (`jina-embeddings-v3`, 512 dimensi), Pinecone,
dan DeepSeek (`deepseek-chat`). Semua perintah berikut dijalankan dari root
repository dengan virtual environment aktif:

```bash
python -m src.main              # pencarian melalui terminal
python -m src.create_vector_db  # ingest CSV ke Pinecone (menulis data)
```

| File | Fungsi |
| --- | --- |
| `main.py` | Input pertanyaan dan output JSON melalui CLI |
| `llm.py` | Konfigurasi/client DeepSeek bersama untuk API dan CLI |
| `search.py` | Mengambil lima dokumen terdekat secara default |
| `utils.py` | Client Pinecone yang dicache, penyusunan konteks dan prompt |
| `embedding.py` | Embedding Jina, batching, timeout dan retry |
| `normalization.py` | Nilai kosong, nama akun, dan URL Instagram yang diizinkan |
| `load_data.py` | Membaca CSV menggunakan Pandas |
| `build_documents.py` | Dokumen dan metadata dari baris CSV, ID dari kolom `id` |
| `vector_store.py` | Menulis dokumen ke index Pinecone |
| `create_vector_db.py` | Alur ingest dari knowledge base final |
| `matching_url.py` | Backfill URL postingan dari raw ke advance CSV berdasarkan caption |
| `sentence_transformer_embedding.py` | Wrapper eksperimen embedding lokal; tidak dipakai aplikasi aktif |

Konfigurasi `.env`, persiapan index, dependensi, dan batasan ingest dijelaskan di
[README utama](../README.md). Jalankan modul dengan `python -m src.<nama_modul>`;
kode tidak memodifikasi `sys.path`.

Ingest memvalidasi kolom, nama tempat, serta ID unik sebelum menghubungi provider.
Input embedding kosong/tidak valid ditolak seluruhnya sebelum batch pertama,
agar pasangan dokumen, ID, dan vektor tidak bergeser. Jumlah, urutan, dimensi,
dan nilai numerik vektor dari Jina diperiksa sebelum dikembalikan untuk upload.
Kegagalan ingest menghasilkan exit code 1; upsert banyak batch dapat bersifat
parsial. Detail timeout/retry dan prosedur mengulang ingest ada di README utama.
