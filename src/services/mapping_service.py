"""
Ürün eşleştirme servisleri
"""

from difflib import SequenceMatcher
from typing import List, Dict


class MappingService:
    """
    Benzer ürün isimlerini eşleştirir.
    """

    def __init__(self):
        pass

    def similarity_score(self, a: str, b: str) -> float:
        """
        İki string arasındaki benzerlik oranı.
        """

        return SequenceMatcher(
            None,
            a.lower(),
            b.lower()
        ).ratio()

    def find_similar_products(
        self,
        current_name: str,
        all_products: List[str],
        threshold: float = 0.6
    ) -> List[Dict]:

        results = []

        for product in all_products:

            if product == current_name:
                continue

            score = self.similarity_score(
                current_name,
                product
            )

            if score >= threshold:

                results.append({
                    "product": product,
                    "score": round(score, 2)
                })

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results
