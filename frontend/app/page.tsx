// app/page.tsx
'use client';
import Image from 'next/image';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setAnswer('');
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error('Error fetching chat:', error);
      setAnswer('Terjadi kesalahan. Silakan coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSubmit();
  };

  const suggestions = [
    'Jajanan sekitar kampus UNY Yogyakarta',
    'Makanan dekat Mangkunegaran Solo',
    'Mie ayam enak di Jogja yang buka malam',
    'Rekomendasi makanan yang buka 24 jam'
  ];

  const sourceAccounts = {
    jogja: [
      '@jogjabikinlaper',
      '@kulinerjogya',
      '@infonongkrongjogja',
      '@melipirkulineran',
    ],
    solo: [
      '@carikulinersolo',
      '@infomakansolo',
      '@solokenyang',
      '@sijajanjalan',
    ],
  };

  return (
    <main className="min-h-screen relative font-sans">
      {/* Gambar Latar Belakang */}
      <div 
        className="absolute inset-0 bg-[#FFFBEB] z-0 bg-cover bg-center" 
        style={{ backgroundImage: `url('/images/background-kuliner.jpg')` }} 
      />
      {/* Overlay Krem Transparan */}
      <div className="absolute inset-0 bg-[#FFFBEB]/70 z-0" />

      {/* Konten Utama */}
      <div className="relative z-10 w-full">
        
        {/* Header */}
        <header className="fixed top-0 left-0 right-0 bg-white/95 shadow-sm px-6 py-4 flex items-center justify-between z-20 backdrop-blur-sm border-b border-gray-100">
          <div className="flex items-center gap-3">
            <Image
              src="/images/logo_v2.svg"
              alt="Logo Kitab Kuliner"
              width={40}
              height={40}
              className="h-10 w-10 object-contain"
              priority
            />
            {/* Menggunakan arbitrary value untuk font serif */}
            <h1 className="text-2xl font-['Playfair_Display',_serif] text-[#033B2B]">Kitab Kuliner</h1>
          </div>
          <nav className="flex items-center gap-7">
            <a href="#" className="text-gray-700 hover:text-[#005D41] text-sm font-medium">Cari</a>
            <a href="#" className="text-gray-700 hover:text-[#005D41] text-sm font-medium">Kategori</a>
            <button className="bg-[#005D41] hover:bg-[#15803D] text-white font-semibold px-6 py-2 rounded-full text-sm transition-colors">
              Tanya Ahli
            </button>
          </nav>
        </header>

        {/* Hero Section */}
        <section className="flex flex-col items-center justify-start pt-40 pb-24 px-4 min-h-[90vh]">
          <div className="text-center mb-12">
            <div className="mb-6 flex justify-center">
               <div className="h-20 w-20 border border-gray-800 rounded-full bg-white/85 p-2 shadow-sm flex items-center justify-center">
                 <Image
                   src="/images/logo_v2.svg"
                   alt="Ikon Kitab Kuliner"
                   width={60}
                   height={60}
                   className="h-14 w-14 object-contain"
                 />
               </div>
            </div>
            <h2 className="text-5xl font-['Playfair_Display',_serif] text-[#033B2B] mb-4 tracking-tight">
              Temukan kuliner yang Anda butuhkan
            </h2>
            <p className="text-xl font-['Playfair_Display',_serif] italic text-gray-500">
              Kelezatan Jogja & Solo, terbuka untuk semua
            </p>
          </div>

          {/* Kotak Pencarian */}
          <div className="w-full max-w-2xl mb-10">
            <div className="flex gap-4">
              <input
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Cari rekomendasi, nama tempat, atau menu..."
                className="flex-1 border-2 border-gray-300 rounded-lg px-5 py-3.5 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-[#005D41] transition-colors bg-white/90 backdrop-blur-sm"
              />
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-[#005D41] hover:bg-[#15803D] disabled:bg-[#005D41]/50 text-white font-semibold px-8 py-3.5 rounded-lg transition-colors text-base"
              >
                {loading ? 'Mencari...' : 'Cari'}
              </button>
            </div>

            {/* Saran Pencarian */}
            <div className="mt-6 text-center text-sm text-gray-600 flex flex-col sm:flex-row sm:items-center sm:justify-center gap-3">
              <span>Coba cari:</span>
              <div className="flex gap-2.5 flex-wrap justify-center">
                {suggestions.map(suggestion => (
                  <button 
                    key={suggestion} 
                    onClick={() => setQuery(suggestion)} 
                    className="border border-gray-300 bg-white/50 hover:bg-white text-gray-600 rounded-full px-4 py-1.5 font-medium transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>

            {/* Jawaban / Loading Box */}
            <div className="mt-8">
              {loading && (
                <div className="p-6 bg-white/80 backdrop-blur-sm border border-[#005D41]/20 rounded-xl flex items-center justify-center gap-3 text-[#005D41] text-base shadow-sm">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  Sedang mencari rekomendasi kuliner terbaik...
                </div>
              )}

              {answer && !loading && (
                <div className="p-6 bg-white border-t-4 border-[#005D41] rounded-xl shadow-md text-gray-800 text-base leading-relaxed prose prose-green max-w-none">
                  <ReactMarkdown>{answer}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Bagian Statistik Bawah */}
        <section className="bg-white border-t border-gray-200 w-full py-16 px-4">
          <div className="text-center text-xs font-bold tracking-widest text-gray-500 uppercase mb-12">
            Database Kuliner Jogja & Solo
          </div>
          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
            <div className="flex flex-col items-center">
              <span className="text-5xl font-['Playfair_Display',_serif] text-gray-900">500+</span>
              <span className="text-sm font-bold text-gray-800 mt-4 mb-1">Rekomendasi Tempat</span>
              <span className="text-sm text-gray-500">Kuliner Legendaris, Instagramable, dan Kaki Lima</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-5xl font-['Playfair_Display',_serif] text-gray-900">1.000+</span>
              <span className="text-sm font-bold text-gray-800 mt-4 mb-1">Menu Terkurasi Food Selebgram</span>
              <span className="text-sm text-gray-500">Gudeg, soto, bakpia, selat, dll</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-5xl font-['Playfair_Display',_serif] text-gray-900">100%</span>
              <span className="text-sm font-bold text-gray-800 mt-4 mb-1">Berbasis AI & Review</span>
              <span className="text-sm text-gray-500">Didukung oleh DeepSeek AI</span>
            </div>
          </div>
        </section>

        {/* Bagian Sumber Data */}
        <section className="relative overflow-hidden bg-gradient-to-b from-[#FFF8E6] via-[#FFFBEB] to-[#F3F9F5] border-t border-[#E4E7D7] w-full py-20 px-4">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[36rem] h-[36rem] rounded-full bg-[#0B6A4A]/10 blur-3xl pointer-events-none" />

          <div className="relative max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <p className="text-xs font-bold tracking-[0.24em] text-[#0B6A4A] uppercase mb-4">
                Sumber Data Terverifikasi
              </p>
              <h3 className="text-4xl md:text-5xl font-['Playfair_Display',_serif] text-[#033B2B] mb-4">
                Akun Referensi Kuliner
              </h3>
              <p className="max-w-2xl mx-auto text-base md:text-lg text-[#456353] leading-relaxed">
                Basis rekomendasi kami disusun dari akun kurasi kuliner terpercaya di Jogja dan Solo.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
              <article className="rounded-3xl border border-[#CFE3D7] bg-white/80 backdrop-blur-sm shadow-[0_14px_38px_rgba(5,65,47,0.08)] p-7 md:p-8">
                <div className="flex items-center gap-3 mb-5">
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#E7F3EC] text-[#0B6A4A] text-xl">
                    YK
                  </span>
                  <div>
                    <h4 className="text-2xl font-['Playfair_Display',_serif] text-[#033B2B]">Yogyakarta</h4>
                    <p className="text-sm text-[#4B6359]">Akun kurator kuliner Jogja</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2.5">
                  {sourceAccounts.jogja.map(account => (
                    <a
                      key={account}
                      href={`https://instagram.com/${account.replace('@', '')}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center rounded-full border border-[#BBD5C7] bg-[#F4FBF7] px-4 py-2 text-sm font-semibold text-[#0B6A4A] hover:bg-[#E8F6EF] transition-colors"
                    >
                      {account}
                    </a>
                  ))}
                </div>
              </article>

              <article className="rounded-3xl border border-[#D9DCC5] bg-white/80 backdrop-blur-sm shadow-[0_14px_38px_rgba(88,67,22,0.08)] p-7 md:p-8">
                <div className="flex items-center gap-3 mb-5">
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#F4F0DC] text-[#705A25] text-xl">
                    SKA
                  </span>
                  <div>
                    <h4 className="text-2xl font-['Playfair_Display',_serif] text-[#033B2B]">Solo</h4>
                    <p className="text-sm text-[#665F47]">Akun kurator kuliner Solo</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2.5">
                  {sourceAccounts.solo.map(account => (
                    <a
                      key={account}
                      href={`https://instagram.com/${account.replace('@', '')}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center rounded-full border border-[#D8CFB2] bg-[#FFF8E2] px-4 py-2 text-sm font-semibold text-[#705A25] hover:bg-[#FBEFCC] transition-colors"
                    >
                      {account}
                    </a>
                  ))}
                </div>
              </article>
            </div>
          </div>
        </section>

      </div>
    </main>
  );
}