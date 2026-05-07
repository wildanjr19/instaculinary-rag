from langchain_core.documents import Document
import pandas as pd


def _safe(val, default=""):
    """Konversi nilai ke string, aman dari NaN."""
    if pd.isna(val):
        return default
    return str(val)


def build_content(row):
    return f"""
Nama : {row['nama_tempat']}
Alamat : {row['alamat']}
Jam_Buka : {row['jam_buka']}
Jam_Tutup : {row['jam_tutup']}
Harga : {row['harga']}
Kategori : {row['kategori']}
Deskripsi : {row['deskripsi']}
Opini : {row['opini']}
URL : {_safe(row.get('url', ''))}
Daerah : {row['daerah']}
Sumber : {row['sumber']}
""".strip()

def create_documents(df):
    docs = []
    ids = []
    for _, row in df.iterrows():
        docs.append(
            Document(
                page_content=build_content(row),
                metadata={
                    "id": str(row["id"]),
                    "kategori": _safe(row["kategori"]),
                    "nama": _safe(row["nama_tempat"]),
                    "deskripsi": _safe(row["deskripsi"]),
                    "opini": _safe(row["opini"]),
                    "url": _safe(row.get("url", "")),
                    "daerah": _safe(row["daerah"]),
                    "sumber": _safe(row["sumber"]),
                }
            )
        )
        # ID deterministik dari kolom 'id' di CSV
        ids.append(str(row["id"]))
    return docs, ids