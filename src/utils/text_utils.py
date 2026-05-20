"""
Metin düzenleme yardımcıları.
"""

import re
import unicodedata


TURKISH_REPLACEMENTS = str.maketrans({
    "ç": "c",
    "Ç": "c",
    "ğ": "g",
    "Ğ": "g",
    "ı": "i",
    "I": "i",
    "İ": "i",
    "ö": "o",
    "Ö": "o",
    "ş": "s",
    "Ş": "s",
    "ü": "u",
    "Ü": "u",
})


def normalize_text(text: str) -> str:
    """Dosya adı gibi metinleri ekranda okunur başlığa çevirir."""
    if not text:
        return ""

    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.title()


def ascii_key(text: str) -> str:
    """Türkçe karakterleri sadeleştirilmiş karşılaştırma anahtarına çevirir."""
    text = (text or "").strip().translate(TURKISH_REPLACEMENTS)
    text = remove_accents(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def slugify(text: str) -> str:
    """SEO uyumlu slug üretir."""
    return ascii_key(text)


def remove_accents(text: str) -> str:
    """Aksan karakterlerini kaldırır."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )
