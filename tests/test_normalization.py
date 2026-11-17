import unittest

from src.normalization import (
    MISSING_INFO, normalize_account, normalize_document_text, normalize_instagram_url, normalize_text,
)


class NormalizationTests(unittest.TestCase):
    def test_missing_values_have_explicit_placeholder(self):
        for value in (None, float("nan"), "", "   ", "NaN", "<NA>"):
            with self.subTest(value=value):
                self.assertEqual(normalize_text(value, MISSING_INFO), MISSING_INFO)
        self.assertEqual(normalize_text("  Rp 15.000  "), "Rp 15.000")

    def test_accounts_have_one_prefix_and_cannot_inject_a_url(self):
        for value in ("instagram @Contoh", "@contoh", "contoh", "@instagram @contoh"):
            with self.subTest(value=value):
                self.assertEqual(normalize_account(value), "@contoh")
        self.assertEqual(normalize_account("@contoh/../../evil"), "")

    def test_source_urls_reject_active_schemes_and_lookalike_hosts(self):
        invalid_urls = [
            "javascript:alert(1)", "data:text/html,example", "//instagram.com/p/abc/",
            "https://instagram.com.evil.example/p/abc/", "https://instagram.com@evil.example/p/abc/",
            "https://evil.example@instagram.com/p/abc/", "https://instagram.com:444/p/abc/",
            "https://instagram.com\\@evil.example/p/abc/", "https://instagram.com/p/abc/\n",
            "https://instagram.com/p/%0a/", "https://[invalid",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertEqual(normalize_instagram_url(url), "")
                self.assertEqual(normalize_instagram_url(url, "@contoh"), "https://instagram.com/contoh")

    def test_real_post_paths_keep_the_post_and_remove_tracking(self):
        for kind in ("p", "reel", "reels", "tv"):
            with self.subTest(kind=kind):
                self.assertEqual(
                    normalize_instagram_url(f"https://www.instagram.com/{kind}/AbC_123-/?igsh=tracking#fragment"),
                    f"https://instagram.com/{kind}/AbC_123-/",
                )

    def test_legacy_document_fields_are_cleaned_without_rewriting_description(self):
        text = "Nama : Soto\nHarga : nan\nJam_Buka : None\nSumber : instagram @contoh\nURL : nan\nDeskripsi : Soto hangat: enak."
        normalized = normalize_document_text(text, "@contoh")
        self.assertIn(f"Harga : {MISSING_INFO}\n", normalized)
        self.assertIn(f"Jam_Buka : {MISSING_INFO}\n", normalized)
        self.assertIn("Sumber : @contoh\n", normalized)
        self.assertIn("URL : https://instagram.com/contoh\n", normalized)
        self.assertIn("Deskripsi : Soto hangat: enak.", normalized)
