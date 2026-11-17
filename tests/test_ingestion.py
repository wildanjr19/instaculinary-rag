import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src import create_vector_db
from src.build_documents import build_content, create_documents
from src.load_data import load_csv
from src.utils import build_context
from src.vector_store import build_vector_store


def place(**overrides):
    row = {
        "id": "001", "nama_tempat": "Soto Solo", "alamat": "Solo", "jam_buka": "07:00",
        "jam_tutup": "14:00", "harga": "Rp 15.000", "kategori": "Soto", "deskripsi": "Soto hangat.",
        "opini": "Gurih.", "sumber": "instagram @contoh", "daerah": "Surakarta", "url": "",
    }
    row.update(overrides)
    return row


class IngestionTests(unittest.TestCase):
    def test_csv_ids_preserve_leading_zeroes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            pd.DataFrame([place()]).to_csv(path, index=False)
            docs, ids = create_documents(load_csv(path))
        self.assertEqual(ids, ["001"])
        self.assertEqual(docs[0].metadata["id"], "001")

    def test_missing_columns_fail_with_clear_validation_error(self):
        frame = pd.DataFrame([place()]).drop(columns=["alamat"])
        with self.assertRaisesRegex(ValueError, "alamat"):
            create_documents(frame)

    def test_empty_missing_and_duplicate_ids_are_rejected(self):
        frames = [pd.DataFrame(columns=place().keys()), pd.DataFrame([place(id=None)]),
                  pd.DataFrame([place(id=" ")]), pd.DataFrame([place(), place(id=" 001 ")])]
        for frame in frames:
            with self.subTest(rows=len(frame)), self.assertRaises(ValueError):
                create_documents(frame)

    def test_missing_place_name_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "nama_tempat"):
            create_documents(pd.DataFrame([place(nama_tempat=None)]))

    def test_missing_details_and_account_are_normalized(self):
        row = place(harga=float("nan"), jam_buka=None)
        content = build_content(row)
        self.assertIn("Harga : Informasi tidak tersedia", content)
        self.assertIn("Jam_Buka : Informasi tidak tersedia", content)
        docs, _ = create_documents(pd.DataFrame([row]))
        self.assertEqual(docs[0].metadata["sumber"], "@contoh")
        # Konteks juga harus mendukung metadata dari index lama.
        docs[0].metadata["sumber"] = "instagram @contoh"
        self.assertIn("Sumber Akun: @contoh\n", build_context(docs))

    def test_optional_post_url_falls_back_to_account(self):
        frame = pd.DataFrame([place()]).drop(columns=["url"])
        docs, _ = create_documents(frame)
        self.assertEqual(docs[0].metadata["url"], "https://instagram.com/contoh")

    def test_document_id_mismatch_is_rejected_before_upload(self):
        docs, _ = create_documents(pd.DataFrame([place()]))
        with patch.dict(os.environ, {"PINECONE_API_KEY": "offline-test-key"}), patch(
            "src.vector_store.PineconeVectorStore.from_documents"
        ) as upload:
            with self.assertRaisesRegex(ValueError, "Jumlah dokumen"):
                build_vector_store(docs, [], "unused", object())
        upload.assert_not_called()

    def test_failed_ingest_returns_nonzero_status(self):
        with patch.object(create_vector_db, "load_csv", return_value=pd.DataFrame([place()])), patch.object(
            create_vector_db, "JinaEmbedding"
        ), patch.object(create_vector_db, "build_vector_store", side_effect=RuntimeError("offline upload failure")), contextlib.redirect_stdout(
            io.StringIO()
        ), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(create_vector_db.main(), 1)
