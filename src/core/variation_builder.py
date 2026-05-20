"""
Variation üretim sistemi
"""


class VariationBuilder:
    """
    Renk ve beden varyasyonlarını oluşturur.
    """

    def __init__(self):

        self.default_sizes = [
            "S",
            "M",
            "L",
            "XL"
        ]

    def build_variations(
        self,
        color: str,
        sizes=None
    ):

        if sizes is None:
            sizes = self.default_sizes

        variations = []

        for size in sizes:

            variations.append({
                "color": color,
                "size": size
            })

        return variations
