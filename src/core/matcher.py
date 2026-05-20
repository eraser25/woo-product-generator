"""
Benzer ürün eşleştirme sistemi
"""

from difflib import SequenceMatcher
from typing import List, Dict


class ProductMatcher:
    """
    Benzer ürün isimlerini bulur.
    """

    def __init__(self):
        pass

    def similarity(
        self,
        a: str,
        b: str
    ) -> float:

        return SequenceMatcher(
            None,
            a.lower(),
            b.lower()
        ).ratio()

    def find_matches(
        self,
        target: str,
        products: List[str],
        threshold: float = 0.6
    ) -> List[Dict]:

        matches = []

        for product in products:

            score = self.similarity(
                target,
                product
            )

            if score >= threshold:

                matches.append({
                    "product": product,
                    "score": round(score, 2)
                })

        matches.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return matches
