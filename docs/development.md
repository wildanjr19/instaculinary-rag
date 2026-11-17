# Pengembangan dan pengujian

[Kembali ke README](../README.md)

## Menjalankan secara lokal

Prasyarat:

- Python **3.11+**; versi dependensi Python mengikuti environment lokal yang diverifikasi.
- Node.js **20.9+** dan npm untuk Next.js 16.
- API key DeepSeek, Jina AI, dan Pinecone yang masih berlaku.
- Index Pinecone yang sudah tersedia dengan **512 dimensi**, berisi dokumen hasil
  ingest menggunakan model embedding yang sama dengan query.

Jalankan perintah berikut dari root repository.

### 1. Instal backend

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Daftar dependensi aplikasi tersedia di `pyproject.toml`.

### 2. Atur environment

Untuk setup baru, salin `.env.example` menjadi `.env` di root. Jika `.env` sudah
ada, cukup lengkapi variabelnya. Isi tiga API key:

```dotenv
DEEPSEEK_API_KEY=isi_api_key_deepseek
JINA_AI_API_KEY=isi_api_key_jina
PINECONE_API_KEY=isi_api_key_pinecone
PINECONE_INDEX_NAME=instaculinary-data
```

`PINECONE_INDEX_NAME` opsional. API key disimpan di environment backend.

Untuk frontend, salin `frontend/.env.example` menjadi `frontend/.env.local` jika
file tersebut belum ada:

```dotenv
BACKEND_URL=http://localhost:8000
```

URL ini diakses oleh server Next.js. Jika backend berada di container atau host
lain, gunakan alamat yang dapat dijangkau dari server Next.js. API key tetap
berada di environment backend.

### 3. Jalankan backend

Dengan virtual environment aktif, dari root:

```bash
python -m uvicorn backend.api:app --reload --port 8000
```

- Status proses: <http://localhost:8000/>
- Dokumentasi API: <http://localhost:8000/docs>

### 4. Jalankan frontend

Di terminal lain:

```bash
cd frontend
npm ci
npm run dev
```

Buka <http://localhost:3000>. Frontend mengirim permintaan ke route Next.js,
kemudian route tersebut meneruskannya ke backend.

### 5. CLI (opsional)

Dengan virtual environment aktif, dari root:

```bash
python -m src.main
```

CLI menggunakan retrieval, prompt, dan konfigurasi DeepSeek yang sama dengan web.

## Dependensi dan environment

`requirements.txt` menginstal proyek secara editable. Daftar dependensi aplikasi
dan versi langsungnya ditetapkan di `pyproject.toml`, sehingga tidak ada dua daftar
yang harus diperbarui terpisah. Dependensi transitif belum dikunci dalam lockfile.

`PINECONE_INDEX_NAME` opsional. Backend, CLI, dan script ingest membaca `.env`
dari root proyek. Variabel dari shell atau deployment memiliki prioritas atas
isi `.env`. Kredensial diperiksa saat layanan terkait dipakai; `GET /` hanya
menunjukkan proses API hidup, bukan menguji koneksi ke provider.

## Verifikasi lokal

Instal dependensi pengujian dan jalankan dari root:

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python -m pip check
```

Tes mencakup kontrak HTTP, kegagalan retrieval/generasi, validasi respons AI,
konkurensi, timeout/retry, validasi ingest/embedding, normalisasi sumber, serta
pemuatan environment. Panggilan provider dimock; tes tidak
membuktikan API key atau index eksternal masih aktif.

Pemeriksaan frontend, dari `frontend/`:

```bash
npm run lint
npx tsc --noEmit --incremental false
npm run build
npm run test:proxy
```

Build memerlukan akses Google Fonts karena layout memakai `next/font/google`.

## Struktur kode

```text
backend/api.py               Endpoint status dan pencarian rekomendasi
config/config.py             Root path, .env, index dan dimensi embedding
src/llm.py                   Client DeepSeek bersama untuk backend dan CLI
src/search.py                Retrieval dokumen
src/utils.py                 Koneksi Pinecone yang dicache, konteks dan prompt
src/embedding.py             Client embedding Jina dengan batching/retry
src/build_documents.py       Konversi baris CSV menjadi dokumen dan metadata
src/vector_store.py          Upsert dokumen ke Pinecone
src/create_vector_db.py      Entry point ingest
src/main.py                  Entry point CLI
frontend/app/page.tsx        Halaman pencarian dan kartu rekomendasi
frontend/app/api/chat/route.ts  Proxy Next.js ke FastAPI
tests/                       Tes backend dan konfigurasi
.github/workflows/ci.yaml      Pemeriksaan otomatis saat push dan pull request
.github/workflows/deploy.yaml  Deployment VPS yang hanya dipicu manual
```

## CI

Push dan pull request menjalankan workflow **CI**, tanpa deployment:

- **Backend tests:** Python 3.11, instalasi aplikasi beserta extra `dev`,
  pemeriksaan dependensi, dan seluruh tes Python.
- **Frontend checks:** Node.js 24, `npm ci`, lint, TypeScript, build produksi,
  dan tes integrasi proxy dengan backend tiruan.

CI tidak memerlukan dataset, `.env`, atau API key provider. Build tetap
mengunduh font dari Google Fonts. Pemeriksaan terbaru membatalkan run CI lama
yang masih berjalan pada ref yang sama. CI tidak menghubungi VPS dan tidak
menjalankan ingest Pinecone.
