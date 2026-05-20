"""
Dosya adı ayrıştırma sistemi
"""

from pathlib import Path
from typing import Dict


class FileParser:
    """
    Dosya adından ürün adı ve renk ayırır.
    """

    def __init__(self):
        pass

    def parse_filename(self, filename: str) -> Dict:

        stem = Path(filename).stem

        parts = stem.split("_")

        if len(parts) < 2:

            return {
                "success": False,
                "filename": filename,
                "product_name": "",
                "color": "",
                "error": "Dosya adı formatı hatalı"
            }

        color = parts[-1]

        product_name = " ".join(parts[:-1])

        return {
            "success": True,
            "filename": filename,
            "product_name": product_name.title(),
            "color": color.title()
        }
