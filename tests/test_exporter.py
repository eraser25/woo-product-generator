from src.exporters.woocommerce_csv import WooCommerceCSVExporter


def test_exporter_builds_parent_and_variations():
    exporter = WooCommerceCSVExporter()
    df = exporter.build_rows(
        mappings={
            "space": {
                "product_name": "Space Cat",
                "category": "Tişört",
                "image_urls": "",
                "colors": [
                    {"name": "Beyaz", "code": "BYZ", "image_urls": "https://site.test/beyaz.jpg"},
                    {"name": "Siyah", "code": "SYH", "image_urls": "https://site.test/siyah.jpg"},
                ],
            }
        },
        product_data={
            "regular_price": 399.9,
            "sale_price": 349.9,
            "stock": 5,
            "short_description": "Kısa",
            "description": "Uzun",
        },
        sizes=["S", "M"],
        brand_code="KYX",
        product_type_code="TS",
        start_id=10,
        product_name_suffix="Baskılı Tişört",
    )

    assert len(df) == 5
    assert list(df["ID"]) == ["P0010", "P0011", "P0012", "P0013", "P0014"]
    assert df.iloc[0]["Type"] == "variable"
    assert df.iloc[0]["Name"] == "Space Cat Baskılı Tişört"
    assert df.iloc[0]["Attribute 1 value(s)"] == "Beyaz, Siyah"
    assert df.iloc[1]["Type"] == "variation"
    assert df.iloc[1]["Parent"] == "KYX-TS-0010"
    assert df.iloc[1]["SKU"] == "KYX-TS-0010-BYZ-S"
    assert df.iloc[1]["Images"] == "https://site.test/beyaz.jpg"


def test_exporter_does_not_duplicate_title_suffix():
    exporter = WooCommerceCSVExporter()

    df = exporter.build_rows(
        mappings={
            "space": {
                "product_name": "Space Cat Baskılı Tişört",
                "category": "Tişört",
                "colors": [{"name": "Beyaz", "code": "BYZ", "image_urls": ""}],
            }
        },
        product_data={},
        sizes=["S"],
        product_name_suffix="Baskılı Tişört",
    )

    assert df.iloc[0]["Name"] == "Space Cat Baskılı Tişört"


def test_exporter_allows_empty_or_custom_product_suffix():
    exporter = WooCommerceCSVExporter()
    mappings = {
        "mug": {
            "product_name": "Space Cat",
            "category": "Kupalar",
            "colors": [{"name": "Beyaz", "code": "BYZ", "image_urls": ""}],
        }
    }

    no_suffix = exporter.build_rows(
        mappings=mappings,
        product_data={},
        sizes=["Standart"],
        product_name_suffix="",
    )
    custom_suffix = exporter.build_rows(
        mappings=mappings,
        product_data={},
        sizes=["Standart"],
        product_name_suffix="Seramik Kupa",
    )

    assert no_suffix.iloc[0]["Name"] == "Space Cat"
    assert custom_suffix.iloc[0]["Name"] == "Space Cat Seramik Kupa"


def test_exporter_supports_dynamic_attributes():
    exporter = WooCommerceCSVExporter()

    df = exporter.build_rows(
        mappings={
            "shoe": {
                "product_name": "Runner",
                "category": "Ayakkabı",
                "colors": [{"name": "Siyah", "code": "SYH", "image_urls": "https://site.test/siyah.jpg"}],
            }
        },
        product_data={},
        sizes=[],
        attributes=[
            {"name": "Renk", "values": ["Siyah"], "global": 1},
            {"name": "Ayak Numarası", "values": ["42", "43"], "global": 1},
            {"name": "Yaka Tipi", "values": ["Düz"], "global": 1},
        ],
    )

    assert "Attribute 3 name" in df.columns
    assert len(df) == 3
    assert df.iloc[0]["Attribute 2 name"] == "Ayak Numarası"
    assert df.iloc[1]["Images"] == "https://site.test/siyah.jpg"


def test_exporter_update_mode_preserves_parent_id_and_sku():
    exporter = WooCommerceCSVExporter()

    df = exporter.build_rows(
        mappings={
            "mug": {
                "product_name": "Space Cat",
                "category": "Kupalar",
                "existing_parent_id": "123",
                "existing_parent_sku": "OLD-SKU",
                "colors": [{"name": "Beyaz", "code": "BYZ", "image_urls": ""}],
            }
        },
        product_data={},
        sizes=["Standart"],
        product_mode="Mevcut ürünü güncelle",
    )

    assert df.iloc[0]["ID"] == "123"
    assert df.iloc[0]["SKU"] == "OLD-SKU"
    assert df.iloc[1]["Parent"] == "OLD-SKU"
