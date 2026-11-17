from langchain_core.documents import Document

from src.normalization import MISSING_INFO, normalize_account, normalize_instagram_url, normalize_text

_CONTENT_FIELDS = (
    ("Nama", "nama_tempat"), ("Alamat", "alamat"), ("Jam_Buka", "jam_buka"),
    ("Jam_Tutup", "jam_tutup"), ("Harga", "harga"), ("Kategori", "kategori"),
    ("Deskripsi", "deskripsi"), ("Opini", "opini"), ("URL", "url"),
    ("Daerah", "daerah"), ("Sumber", "sumber"),
)
_REQUIRED_COLUMNS = {column for _, column in _CONTENT_FIELDS if column != "url"} | {"id"}


def build_content(row):
    source = normalize_account(row.get("sumber"))
    url = normalize_instagram_url(row.get("url"), source)
    values = {column: normalize_text(row.get(column), MISSING_INFO) for _, column in _CONTENT_FIELDS}
    values.update(sumber=source or MISSING_INFO, url=url or MISSING_INFO)
    return "\n".join(f"{label} : {values[column]}" for label, column in _CONTENT_FIELDS)


def create_documents(df):
    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Kolom CSV wajib belum tersedia: {', '.join(sorted(missing))}.")
    if not df.columns.is_unique:
        raise ValueError("Nama kolom CSV tidak boleh duplikat.")
    if df.empty:
        raise ValueError("Knowledge base tidak boleh kosong.")
    ids = df["id"].map(normalize_text).tolist()
    if any(not doc_id for doc_id in ids):
        raise ValueError("Kolom id wajib terisi pada setiap baris.")
    if len(set(ids)) != len(ids):
        raise ValueError("Kolom id harus unik, termasuk setelah spasi dibersihkan.")
    if not df["nama_tempat"].map(normalize_text).all():
        raise ValueError("Kolom nama_tempat wajib terisi pada setiap baris.")

    docs = []
    for doc_id, (_, row) in zip(ids, df.iterrows()):
        source = normalize_account(row["sumber"])
        docs.append(Document(
            page_content=build_content(row),
            metadata={
                "id": doc_id,
                "kategori": normalize_text(row["kategori"]),
                "nama": normalize_text(row["nama_tempat"]),
                "deskripsi": normalize_text(row["deskripsi"]),
                "opini": normalize_text(row["opini"]),
                "url": normalize_instagram_url(row.get("url"), source),
                "daerah": normalize_text(row["daerah"]),
                "sumber": source,
            },
        ))
    return docs, ids
