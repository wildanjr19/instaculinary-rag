# Deployment

[Kembali ke README](../README.md)

Workflow **Deploy Culinary RAG (manual)** memakai `workflow_dispatch`; push ke
branch mana pun, termasuk `main`, tidak memicu deployment. Setelah perubahan
workflow masuk ke default branch, deployment kelak bisa dipicu dari
**Actions → Deploy Culinary RAG (manual) → Run workflow**, dengan branch `main`.
Job deployment dilewati jika branch lain dipilih.
Lihat [panduan manual workflow GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Saat dipicu manual, workflow melakukan SSH ke VPS, memperbarui source/dependensi,
membangun frontend, lalu menjalankan atau me-restart proses `culinary-backend`
dan `culinary-frontend` melalui PM2. Workflow memerlukan secrets `SSH_HOST`,
`SSH_USER`, dan `SSH_KEY`, serta direktori server `/home/ubuntu/culinary-rag`.
Konfigurasi deployment lama disimpan untuk disesuaikan saat VPS baru siap.

Workflow tersebut mengasumsikan VPS sudah disiapkan. Provisioning server,
konfigurasi reverse proxy/TLS, dan backup data belum tersedia lengkap di repo.
File `.env` root dan `frontend/.env.local` harus disediakan di server. Menjalankan
workflow saja tidak memulihkan data atau konfigurasi dari VPS yang hilang.

Untuk menjalankan frontend hasil build secara lokal: `npm run build` lalu
`npm start` dari `frontend/`. Backend produksi dapat dijalankan dengan
`python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000`.
