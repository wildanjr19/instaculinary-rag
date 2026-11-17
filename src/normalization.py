"""Normalisasi data kuliner dan tautan sumber tanpa akses jaringan."""
import re
from urllib.parse import urlsplit, urlunsplit

MISSING_INFO = "Informasi tidak tersedia"
_EMPTY_VALUES = {"", "nan", "none", "null", "<na>", "nat"}
_INSTAGRAM_HOSTS = {"instagram.com", "www.instagram.com", "m.instagram.com"}
_DOCUMENT_LABELS = {
    "Nama", "Alamat", "Jam_Buka", "Jam_Tutup", "Harga", "Kategori",
    "Deskripsi", "Opini", "URL", "Daerah", "Sumber",
}


def normalize_text(value, default="") -> str:
    text = "" if value is None else str(value).strip()
    return default if text.lower() in _EMPTY_VALUES else text


def normalize_account(value) -> str:
    match = re.fullmatch(r"(?:@?instagram\s+)?@?([a-z0-9._]{1,30})", normalize_text(value), re.IGNORECASE)
    return f"@{match.group(1).lower()}" if match else ""


def normalize_instagram_url(value, source="") -> str:
    raw = "" if value is None else str(value)
    text = normalize_text(value)
    # URL hasil dataset/LLM masuk ke href browser: hanya izinkan sumber Instagram.
    if (
        text and not any(ord(char) < 32 for char in raw)
        and not any(char.isspace() or char == "\\" for char in text)
    ):
        try:
            parsed = urlsplit(text)
            if (
                parsed.scheme.lower() in {"https", "http"}
                and parsed.netloc.lower() in _INSTAGRAM_HOSTS
                and re.fullmatch(r"/(?:[a-z0-9._]{1,30}|(?:p|reel|reels|tv)/[a-z0-9_-]+)/?", parsed.path, re.IGNORECASE)
            ):
                return urlunsplit(("https", "instagram.com", parsed.path, "", ""))
        except ValueError:
            pass
    account = normalize_account(source)
    return f"https://instagram.com/{account[1:]}" if account else ""


def normalize_document_text(content: str, source="") -> str:
    """Bersihkan label lama saat retrieval tanpa mengubah isi index Pinecone."""
    lines = []
    for line in content.splitlines():
        label, separator, value = line.partition(":")
        label = label.strip()
        if separator and label in _DOCUMENT_LABELS:
            if label == "Sumber":
                value = normalize_account(value) or MISSING_INFO
            elif label == "URL":
                value = normalize_instagram_url(value, source) or MISSING_INFO
            else:
                value = normalize_text(value, MISSING_INFO)
            line = f"{label} : {value}"
        lines.append(line)
    return "\n".join(lines)
