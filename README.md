# 🍜 Kitab Kuliner — Culinary RAG

<p align="center">
  <img src="assets/homepage.png" alt="Halaman Kitab Kuliner" width="800" />
</p>

Kitab Kuliner memberikan rekomendasi kuliner Yogyakarta dan Surakarta (Solo)
berdasarkan data Instagram food vlogger. Proyek ini dikembangkan saat magang
sebagai Data Scientist di DataIns.

Pengguna mengirim satu pertanyaan dan menerima kartu rekomendasi berisi nama
tempat, alamat, jam buka, harga, kategori, deskripsi, serta tautan sumber Instagram.
Saat ini setiap pencarian berdiri sendiri; belum ada riwayat percakapan.

## Tentang proyek

Proyek ini mengolah informasi kuliner dari Instagram menjadi data yang dapat
dicari melalui pertanyaan sehari-hari. Cakupannya meliputi pengolahan data,
pencarian informasi dengan RAG, API backend, dan antarmuka web untuk menampilkan
rekomendasi.

## Yang ditawarkan

- Pencarian lewat bahasa sehari-hari. Pengguna dapat menulis pertanyaan untuk
  mencari tempat makan, misalnya: "Ada rekomendasi gudeg di Yogyakarta?"
- Rekomendasi dengan konteks lokal, berfokus pada kuliner Yogyakarta dan Solo
  dari data Instagram food vlogger.
- Informasi tempat makan dalam kartu yang memuat alamat, jam buka, harga,
  kategori, dan deskripsi, sehingga hasil pencarian mudah dibaca.
- Tautan sumber Instagram pada rekomendasi agar pengguna dapat menelusuri
  informasi asalnya.

## Cara kerja

Kitab Kuliner memakai Retrieval-Augmented Generation (RAG): aplikasi mencari
informasi yang relevan dari data kuliner sebelum menyusun jawaban.

1. Data Instagram melalui tahap ekstraksi, kategorisasi, dan pengolahan deskripsi
   serta opini hingga menjadi knowledge base.
2. Jina AI mengubah data tersebut menjadi representasi numerik yang disebut
   embedding, lalu aplikasi menyimpannya di Pinecone untuk pencarian.
3. Saat pengguna mengirim pertanyaan, aplikasi mencari lima dokumen yang paling
   relevan di Pinecone.
4. DeepSeek menggunakan informasi hasil pencarian untuk menyusun jawaban.
   Aplikasi menampilkannya sebagai kartu rekomendasi beserta tautan sumber.

Data tempat makan perlu diproses dan diunggah ke Pinecone sebelum dapat digunakan
dalam pencarian. Perubahan pada CSV saja belum memperbarui jawaban aplikasi.

## Teknologi utama

| Bagian | Teknologi |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | FastAPI, Pydantic, Uvicorn |
| Integrasi RAG | LangChain |
| Pencarian data | Jina AI untuk embedding dan Pinecone untuk penyimpanan vektor |
| Penyusunan jawaban | DeepSeek |
| Pengolahan data | Pandas dan Jupyter Notebook |

## Status dan batasan

Dataset belum dipublikasikan. Repository ini tidak menyertakan CSV, notebook,
model lokal, atau kredensial. Pencarian dan penyusunan jawaban memerlukan layanan
eksternal serta index Pinecone yang sudah berisi data.

- Setiap pencarian berdiri sendiri; belum ada riwayat percakapan.
- Pencarian masih berdasarkan kemiripan informasi, tanpa filter terstruktur
  untuk wilayah, harga, atau jam buka dan tanpa tahap pemeringkatan ulang
  (reranker).
- Login, panel admin, database SQLite, dan CRUD belum diimplementasikan.
- Integrasi Google Maps dan perluasan wilayah masih berupa rencana.

## Dokumentasi teknis

- [Arsitektur aplikasi](docs/architecture.md): konfigurasi model, alur pencarian,
  timeout, dan penanganan request.
- [Data dan ingest Pinecone](docs/data.md): tahapan pengolahan data, format CSV,
  dan pembaruan index.
- [Pengembangan dan pengujian](docs/development.md): cara menjalankan secara
  lokal, dependensi, struktur kode, pengujian, dan CI.
- [Deployment](docs/deployment.md): workflow manual dan kebutuhan VPS.

Tampilan terinspirasi dari [pasal.id](https://pasal.id) oleh
[@ilhamfputra](https://github.com/ilhamfputra).
