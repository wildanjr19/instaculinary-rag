# src/ Directory

Folder `src/` berisi kode aplikasi utama untuk proyek RAG (Retrieval-Augmented Generation). Kode-kode di sini menangani pemrosesan data, embedding, penyimpanan vektor, dan fungsi pencarian.

## Struktur Folder

```
src/
├── build_documents.py      # Script untuk membangun dokumen dari data
├── load_data.py            # Script untuk memuat data dari file CSV
├── main.py                 # Script utama untuk menjalankan aplikasi RAG
├── search.py               # Script untuk fungsi pencarian dan retrieval
├── sentence_transformer_embedding.py  # Script untuk embedding menggunakan Sentence Transformer
├── utils.py                # Utilitas umum dan fungsi helper
├── vector_store.py         # Script untuk mengelola penyimpanan vektor (ChromaDB)
└── __pycache__/            # Cache bytecode Python (dihasilkan otomatis)
```

## Penjelasan Script

### build_documents.py
Script ini bertanggung jawab untuk membangun dokumen dari data mentah. Mengubah data CSV menjadi format dokumen yang dapat digunakan untuk embedding dan penyimpanan vektor.

### load_data.py
Script untuk memuat data dari berbagai sumber, terutama file CSV di folder `data/`. Menangani preprocessing awal dan validasi data sebelum diproses lebih lanjut.

### main.py
Script utama yang mengintegrasikan semua komponen RAG. Menjalankan pipeline lengkap dari pemuatan data hingga pencarian, dan dapat digunakan sebagai entry point aplikasi.

### search.py
Mengimplementasikan fungsi pencarian dan retrieval. Menggunakan embedding untuk menemukan dokumen relevan berdasarkan query pengguna, dan menghasilkan respons menggunakan model LLM.

### sentence_transformer_embedding.py
Menangani embedding teks menggunakan model Sentence Transformer (multilingual-e5-small). Mengubah teks menjadi vektor numerik untuk penyimpanan dan pencarian.

### utils.py
Berisi fungsi-fungsi utilitas umum seperti logging, validasi, dan helper functions yang digunakan di berbagai script lainnya.

### vector_store.py
Mengelola interaksi dengan database vektor (ChromaDB). Menangani penyimpanan, pengambilan, dan pencarian vektor dalam database.

### __pycache__/
Folder ini dihasilkan otomatis oleh Python untuk menyimpan bytecode compiled. Tidak perlu diedit atau di-commit ke version control.
