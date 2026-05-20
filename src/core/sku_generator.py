"""
SKU üretim sistemi
"""


class SKUGenerator:
    """
    Parent ve variation SKU üretir.
    """

    def __init__(
        self,
        brand_code="KYX",
        product_type_code="TS"
    ):

        self.brand_code = brand_code
        self.product_type_code = product_type_code

    def generate_parent_sku(
        self,
        product_index: int
    ) -> str:

        return (
            f"{self.brand_code}-"
            f"{self.product_type_code}-"
            f"{product_index:04d}"
        )

    def generate_variation_sku(
        self,
        parent_sku: str,
        color_code: str,
        size: str
    ) -> str:

        return (
            f"{parent_sku}-"
            f"{color_code}-"
            f"{size}"
        )
