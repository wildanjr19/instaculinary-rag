# Arsitektur aplikasi

[Kembali ke README](../README.md)

## Stack dan alur pencarian

| Bagian | Teknologi |
| --- | --- |
| Frontend | Next.js 16.1.6, React 19.2.3, TypeScript, Tailwind CSS 4 |
| Backend | FastAPI, Pydantic, Uvicorn |
| Integrasi RAG | LangChain Core, LangChain OpenAI, LangChain Pinecone |
| Embedding | Jina AI API, `jina-embeddings-v3`, 512 dimensi |
| Vector database | Pinecone, default index `instaculinary-data` |
| Generasi jawaban | DeepSeek API, `deepseek-chat`, temperature 0.3 |
| Pengolahan data | Pandas dan Jupyter Notebook |

```text
Pertanyaan → Next.js /api/chat → FastAPI /api/chat
           → embedding query Jina → lima dokumen terdekat di Pinecone
           → konteks dan prompt → DeepSeek → JSON → kartu rekomendasi

CSV knowledge base → dokumen dengan ID deterministik → Jina → upsert ke Pinecone
```

Pencarian dan generasi jawaban menggunakan layanan eksternal. ChromaDB dan
embedding lokal `multilingual-e5-small` adalah bagian eksperimen lama, bukan
jalur aplikasi aktif. Wrapper embedding lokal masih tersedia di
`src/sentence_transformer_embedding.py`.

Wrapper embedding lokal memerlukan extra `pip install -e ".[local-embedding]"`
  dan model yang disediakan sendiri; instalasi utama tidak mengunduh model lokal.

## Batas waktu dan penanganan request

- Operasi SDK sinkron di endpoint chat berjalan melalui thread pool FastAPI,
  sehingga tidak menahan ASGI event loop dan endpoint status.
- Jina memakai timeout connect 5 detik dan read 15 detik per percobaan, maksimal
  tiga percobaan dengan backoff. Retry hanya untuk timeout, gangguan koneksi,
  HTTP 429, dan HTTP 500/502/503/504. Error kredensial, payload, TLS, dan respons
  embedding yang tidak valid langsung gagal. Redirect tidak diikuti.
- DeepSeek memakai timeout 45 detik dan retry otomatis SDK dimatikan.
- Proxy Next.js menunggu maksimal 150 detik. Atur `BACKEND_TIMEOUT_MS` di
  `frontend/.env.local` jika perlu; nilai harus integer positif. Timeout berlaku
  juga ketika membaca body respons backend. Redirect backend ditolak.
- Timeout Jina/DeepSeek dan proxy menghasilkan HTTP 504 dengan pesan umum.
  Kegagalan HTTP/koneksi Jina menghasilkan HTTP 502; detail tetap di log server.

Timeout tersebut adalah batas tunggu pada lapisan terkait, bukan deadline atomik
seluruh pipeline. Pinecone masih memakai perilaku timeout/retry bawaan SDK.
Abort pada proxy tidak menghentikan thread yang sedang bekerja di backend.
Kapasitas thread pool, rate limit, dan batas body di reverse proxy perlu diatur
ketika menyiapkan deployment publik.

Browser menggunakan route Next.js pada origin yang sama, sehingga middleware
CORS backend tidak diaktifkan. Tautan sumber dari dataset maupun respons AI
dibatasi ke URL HTTPS Instagram; query tracking dan fragment URL dibuang.
