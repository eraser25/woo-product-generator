"""
Renk ayrıştırma sistemi.
"""

from src.utils.text_utils import ascii_key


class ColorParser:
    """Renkleri standart hale getirir."""

    def __init__(self):
        self.color_map = {
            "beyaz": {"name": "Beyaz", "code": "BYZ"},
            "siyah": {"name": "Siyah", "code": "SYH"},
            "kirmizi": {"name": "Kırmızı", "code": "KRM"},
            "mavi": {"name": "Mavi", "code": "MAV"},
            "yesil": {"name": "Yeşil", "code": "YSL"},
            "gri": {"name": "Gri", "code": "GRI"},
            "lacivert": {"name": "Lacivert", "code": "LCV"},
        }

    def parse(self, color: str):
        key = ascii_key(color)

        if key in self.color_map:
            return self.color_map[key]

        cleaned = (color or "").strip()
        return {
            "name": cleaned.title(),
            "code": ascii_key(cleaned)[:3].upper() or "UNK",
        }
