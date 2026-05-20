"""
Ürün adı düzenleme sistemi
"""

import re


class NameNormalizer:
    """
    Ürün isimlerini normalize eder.
    """

    def __init__(self):
        pass

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        text = text.replace("_", " ")
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text.title()

    def build_product_title(self, product_name: str) -> str:
        base = product_name.strip()

        if base.lower().endswith("baskılı tişört"):
            return base

        return f"{base} Baskılı Tişört"