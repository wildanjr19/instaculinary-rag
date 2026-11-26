# Frontend Instaculinary

Next.js 16.1.6, React 19.2.3, TypeScript, dan Tailwind CSS 4. Memerlukan
Node.js 20.9+ dan npm.

Dari folder ini:

```bash
npm ci
npm run dev
```

Buka <http://localhost:3000>. Untuk setup baru, salin `.env.example` menjadi
`.env.local`; jika sudah ada, lengkapi nilainya:

```dotenv
BACKEND_URL=http://localhost:8000
BACKEND_TIMEOUT_MS=150000
```

Server Next.js meneruskan `POST /api/chat` ke backend FastAPI. `BACKEND_URL`
adalah alamat yang diakses server Next.js. API key provider berada di environment
backend. Cara menjalankan backend ada di [README utama](../README.md).

`BACKEND_TIMEOUT_MS` adalah batas tunggu fetch backend dalam milidetik; default
150.000 dan harus integer positif. Timeout menghasilkan HTTP 504. Redirect dari
backend ditolak. Pembatalan fetch tidak menghentikan pekerjaan thread backend.

- `app/page.tsx`: pencarian, saran pertanyaan, kartu rekomendasi, dan sumber akun.
- `app/api/chat/route.ts`: proxy backend; meneruskan status error backend dan
  mengubah kegagalan koneksi/respons non-JSON menjadi HTTP 502 dengan pesan umum.
- `app/layout.tsx`: metadata, ikon, dan font.

Pemeriksaan:

```bash
npm run lint
npx tsc --noEmit --incremental false
npm run build
npm run test:proxy
```

Build membutuhkan akses Google Fonts melalui `next/font/google`. Untuk
menjalankan hasil build, gunakan `npm start`.

`test:proxy` menjalankan build produksi yang sudah tersedia pada port lokal
sementara dengan backend tiruan. Tes memeriksa penerusan status, timeout sebelum
header maupun saat membaca body, dan penolakan redirect tanpa memakai provider.
