from langchain_core.documents import Document

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
Daerah : {row['daerah']}
Sumber : {row['sumber']}
""".strip()

def create_documents(df):
    docs = []
    for _, row in df.iterrows():
        docs.append(
            Document(
                page_content=build_content(row),
                metadata={
                    "id" : row["id"],
                    "kategori": row["kategori"],
                    "nama": row["nama_tempat"],
                    "deskripsi": row["deskripsi"],
                    "opini": row["opini"],
                    "daerah": row["daerah"],
                    "sumber": row["sumber"],
                }
            )
        )
    return docs