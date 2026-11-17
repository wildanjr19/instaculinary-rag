# Data dan ingest Pinecone

[Kembali ke README](../README.md)

Dataset belum dipublikasikan. Clone repository saja tidak menyertakan CSV,
notebook, model lokal, atau kredensial karena direktori/file tersebut diabaikan Git.
Simpan backup data dan notebook secara terpisah dari VPS dan repository.

Tahapan pengolahan data:

```text
data/01_raw/                       Data scraping Instagram
data/02_intermediate_extraction/   Ekstraksi awal dan kategorisasi
data/03_advance_extraction/        Ekstraksi deskripsi/opini dengan LLM
data/04_knowledge_base/            Knowledge base final
```

File yang dibaca script ingest adalah
`data/04_knowledge_base/knowledge_base_v2.csv`, dengan kolom:

```text
id, sumber, nama_tempat, alamat, jam_buka, jam_tutup, harga,
kategori, deskripsi, opini, url, daerah
```

Jika index perlu diisi atau datanya diperbarui, jalankan dari root:

```bash
python -m src.create_vector_db
```

Perintah tersebut memanggil API Jina dan menulis ke Pinecone; penggunaan dapat
menghabiskan kuota provider. Script tidak membuat index Pinecone. Buat/pastikan
index 512 dimensi terlebih dahulu dan gunakan API key untuk project yang benar.
ID vektor menggunakan `str(id)` dari CSV, sehingga ingest ulang memperbarui ID
yang sama. Baris yang dihapus dari CSV **tidak otomatis dihapus dari Pinecone**.

Sebelum embedding/upload, script memvalidasi kolom wajib, ID yang terisi dan unik,
serta nama tempat yang terisi. ID dibaca sebagai string agar nol di depan tidak
hilang. URL postingan opsional; jika tidak tersedia atau tidak valid, tautan
beralih ke profil akun Instagram yang valid. Nilai kosong diberi penanda
`Informasi tidak tersedia`, dan sumber akun dinormalisasi menjadi `@namaakun`.
Konteks dari dokumen index lama juga dibersihkan saat retrieval.

Ingest mengembalikan exit code 0 jika selesai dan 1 jika gagal. Upload banyak
batch bukan transaksi atomik: kegagalan dapat meninggalkan sebagian batch yang
sudah tertulis. Perbaiki penyebabnya dan ulangi menggunakan ID yang sama.

API pencarian membaca Pinecone, bukan CSV secara langsung. Mengedit CSV saja
belum mengubah jawaban chatbot sampai vektornya diperbarui.
