from src.core.sku_generator import SKUGenerator


def test_sku_generator_formats_parent_and_variation_skus():
    generator = SKUGenerator(brand_code="KYX", product_type_code="TS")

    parent = generator.generate_parent_sku(7)

    assert parent == "KYX-TS-0007"
    assert generator.generate_variation_sku(parent, "BYZ", "M") == "KYX-TS-0007-BYZ-M"
