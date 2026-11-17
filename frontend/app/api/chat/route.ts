// app/api/chat/route.ts
// Proxy Next.js → FastAPI Backend
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const BACKEND_TIMEOUT_MS = Number(process.env.BACKEND_TIMEOUT_MS || 150_000);
if (!Number.isSafeInteger(BACKEND_TIMEOUT_MS) || BACKEND_TIMEOUT_MS <= 0) {
  throw new Error('BACKEND_TIMEOUT_MS harus berupa integer positif.');
}

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { query_summary: 'Permintaan tidak valid.', results: [], error: 'Body harus berupa JSON valid.' },
      { status: 400 }
    );
  }

  const signal = AbortSignal.timeout(BACKEND_TIMEOUT_MS);
  try {
    const res = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal,
      redirect: 'error', // Backend tetap satu tujuan; jangan teruskan body ke redirect lain.
    });

    const data = await res.json();
    if (!res.ok) {
      return NextResponse.json(
        {
          query_summary: data.query_summary || 'Permintaan gagal diproses.',
          results: [],
          error: data.error || 'Periksa pertanyaan Anda dan coba lagi.',
        },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (err) {
    console.error('Proxy error:', err);
    if (signal.aborted) {
      return NextResponse.json(
        { query_summary: 'Pencarian terlalu lama.', results: [], error: 'Batas waktu pencarian terlampaui. Silakan coba lagi.' },
        { status: 504 }
      );
    }
    return NextResponse.json(
      { query_summary: 'Layanan backend tidak tersedia.', results: [], error: 'Tidak dapat memproses jawaban server. Silakan coba lagi.' },
      { status: 502 }
    );
  }
}
