"""
MATCHING URL — Opsi 2 (Backfill)
Mencocokkan kolom `url` dari raw data ke advance data via caption.
Jalankan: python src/matching_url.py
"""
import pandas as pd
import glob
import os

# --- CONFIG ---
RAW_DIR = "data/01_raw"
ADVANCE_DIR = "data/03_advance_extraction"


def build_caption_url_map(raw_dir, source_map):
    """Bangun dictionary {caption: url} dari semua file raw yang punya url."""
    caption_to_url = {}

    for file_prefix, source_name in source_map.items():
        pattern = os.path.join(raw_dir, f"{file_prefix}*.csv")
        files = glob.glob(pattern)

        if not files:
            print(f"  ⚠️  Tidak ditemukan: {file_prefix}*.csv")
            continue

        count = 0
        for f in files:
            df = pd.read_csv(f)
            if "url" not in df.columns:
                print(f"  ⚠️  {os.path.basename(f)} tidak punya kolom 'url', skip")
                continue
            for _, row in df.iterrows():
                caption = row["caption"]
                url = row["url"]
                if pd.notna(caption) and pd.notna(url) and str(caption).strip():
                    caption_to_url[str(caption)] = str(url)
                    count += 1

        print(f"  ✅ {source_name}: {count} URL dari {len(files)} file")

    return caption_to_url


def match_url(caption, caption_to_url, raw_captions_list):
    """
    Cari URL untuk sebuah caption.
    1. Exact match ke dictionary (cepat, akurat untuk caption identik)
    2. Fallback: substring match — cek apakah caption ada di dalam raw caption
    """
    c = str(caption).strip() if pd.notna(caption) else ""
    if not c:
        return None

    # 1. Exact match
    if c in caption_to_url:
        return caption_to_url[c]

    # 2. Substring fallback
    for rc, url in raw_captions_list:
        if c in rc:
            return url

    return None


def match_and_save(advance_path, caption_to_url):
    """Tambahkan kolom 'url' ke file advance, lalu simpan ulang."""
    df = pd.read_csv(advance_path)

    # Buat list (raw_caption, url) untuk substring fallback
    raw_captions_list = list(caption_to_url.items())

    # Mapping (dengan fallback)
    df["url"] = df["caption"].apply(
        lambda c: match_url(c, caption_to_url, raw_captions_list)
    )

    # Statistik per source
    print(f"\n  📊 {os.path.basename(advance_path)}:")
    if "source" in df.columns:
        for source in sorted(df["source"].unique()):
            subset = df[df["source"] == source]
            matched = subset["url"].notna().sum()
            total = len(subset)
            pct = matched / total * 100 if total > 0 else 0
            print(f"     {source}: {matched}/{total} ({pct:.1f}%)")

    total_matched = df["url"].notna().sum()
    total_rows = len(df)
    print(f"     TOTAL   : {total_matched}/{total_rows} ({total_matched/total_rows*100:.1f}%)")

    # Simpan
    df.to_csv(advance_path, index=False)
    print(f"  💾 Tersimpan: {advance_path}")

    return df


def process_region(label, advance_files, source_map):
    """Proses satu region (YK/SKA): build mapping & match ke semua advance file."""
    print("\n" + "=" * 60)
    print(f"MATCHING URL: Raw → Advance ({label})")
    print("=" * 60)

    # 1. Bangun mapping dari raw
    print("\n📥 Membangun mapping caption → url dari raw files...")
    caption_to_url = build_caption_url_map(RAW_DIR, source_map)
    print(f"📦 Total mapping: {len(caption_to_url)} caption → url")

    # 2. Proses tiap advance file
    for adv_file in advance_files:
        adv_path = os.path.join(ADVANCE_DIR, adv_file)
        if not os.path.exists(adv_path):
            print(f"\n  ⚠️  File tidak ditemukan: {adv_path}, skip")
            continue
        print("\n" + "-" * 40)
        print(f"📄 Memproses {adv_file}...")
        match_and_save(adv_path, caption_to_url)

    # 3. Contoh hasil
    print("\n" + "-" * 40)
    print(f"📋 Contoh hasil {label} (5 baris pertama yang punya url):")
    main_adv = os.path.join(ADVANCE_DIR, advance_files[0])
    sample = pd.read_csv(main_adv)
    with_url = sample[sample["url"].notna()]
    for _, row in with_url.head(5).iterrows():
        cap = str(row["caption"])[:80]
        print(f"   [{row['source']}] {cap}...")
        print(f"   → {row['url']}\n")

    print("=" * 60)
    print(f"✅ Selesai! {label} — kolom 'url' telah ditambahkan.")
    print("=" * 60)


# ──── SOURCE MAPS ────

YK_SOURCE_MAP = {
    "raw_yk_jogjabikinlaper":      "instagram @jogjabikinlaper",
    "raw_yk_melipirkulineran":     "instagram @melipirkulineran",
    "raw_yk_kulinerjogya":         "instagram @kulinerjogya",
    # NOTE: infonongkrongjogja TIDAK punya url di raw → tidak bisa dimatch
}

SKA_SOURCE_MAP = {
    "raw_ska_carikulinersolo":     "instagram @carikulinersolo",
    "raw_ska_infomakansolo":       "instagram @infomakansolo",
    "raw_ska_sijajanjalan":        "instagram @sijajanjalan",
    "raw_ska_solodelicious":       "instagram @solodelicious",
    "raw_ska_solokenyang":         "instagram @solokenyang",
}


def main():
    # ── YK ──
    process_region(
        label="YK",
        advance_files=["advance_yk.csv", "advance_yk_infonongkrongjogja.csv"],
        source_map=YK_SOURCE_MAP,
    )

    # ── SKA ──
    process_region(
        label="SKA",
        advance_files=["advance_ska.csv"],
        source_map=SKA_SOURCE_MAP,
    )


if __name__ == "__main__":
    main()
