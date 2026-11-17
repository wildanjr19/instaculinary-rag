# Backend FastAPI

Instal dependensi dan atur `.env` sesuai [README utama](../README.md), lalu
jalankan dari root repository:

```bash
python -m uvicorn backend.api:app --reload --port 8000
```

| Endpoint | Fungsi |
| --- | --- |
| `GET /` | Status proses API; tidak menguji koneksi provider |
| `POST /api/chat` | Body JSON `{"query": "soto di Solo"}` |
| `GET /docs` | Dokumentasi OpenAPI interaktif |

Respons pencarian sukses memakai `query_summary` dan `results`. Hasil kosong
tetap HTTP 200. Kegagalan pipeline memakai HTTP 500 dan pesan umum; detail
exception dicatat di log server. JSON AI dengan struktur rekomendasi yang tidak
valid memakai HTTP 502. Respons AI berupa teks biasa tetap menggunakan fallback
kartu teks yang sudah ada. Query kosong/tidak valid ditolak dengan HTTP 422
sebelum retrieval.

Operasi SDK sinkron pada endpoint chat berjalan di thread pool FastAPI, sehingga
endpoint status tetap dapat merespons ketika retrieval menunggu layanan luar.
Timeout Jina/DeepSeek memakai HTTP 504; kegagalan HTTP/koneksi embedding memakai
HTTP 502. Backend tidak mengaktifkan CORS karena browser menggunakan proxy
Next.js pada origin yang sama.

Sumber akun dinormalisasi menjadi `@namaakun`. Tautan hasil AI divalidasi sebelum
dikirim ke frontend: hanya HTTPS Instagram, dengan fallback profil akun jika URL
tidak valid. Batas waktu dan keterbatasan pembatalan dijelaskan di README utama.

Client DeepSeek dibuat saat diperlukan sehingga endpoint status dapat digunakan
tanpa menghubungi provider. Perubahan kredensial di `.env` memerlukan restart
proses karena konfigurasi dan client dicache.

Tes tanpa panggilan provider:

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
```
