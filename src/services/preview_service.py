"""
Önizleme servisleri.
"""

from typing import Any, Dict, List

import pandas as pd


class PreviewService:
    """CSV oluşturulmadan önce parent ve variation önizlemesi üretir."""

    def build_preview_rows(
        self,
        mappings: Dict[str, Dict[str, Any]],
        product_data: Dict[str, Any],
        sizes: List[str],
        brand_code: str = "KYX",
        product_type_code: str = "TS",
        start_id: int = 1,
    ) -> List[Dict[str, Any]]:
        rows = []
        current_id = start_id

        for _, value in mappings.items():
            product_name = value.get("product_name", "")
            colors = value.get("colors", []) or []
            category = value.get("category", product_data.get("category", ""))
            images = value.get("image_urls", product_data.get("image_urls", ""))

            if not colors:
                continue

            parent_id = f"P{current_id:04d}"
            parent_sku = f"{brand_code}-{product_type_code}-{current_id:04d}"

            rows.append({
                "ID": parent_id,
                "Type": "variable",
                "SKU": parent_sku,
                "Name": product_name,
                "Published": 1,
                "Is featured?": 1,
                "Visibility in catalog": "visible",
                "Short description": product_data.get("short_description", ""),
                "Description": product_data.get("description", ""),
                "Regular price": product_data.get("regular_price", ""),
                "Sale price": product_data.get("sale_price", ""),
                "Categories": category,
                "Images": images,
                "Parent": "",
                "Position": 0,
                "Attribute 1 name": "Renk",
                "Attribute 1 value(s)": ", ".join(
                    [c.get("name", "") for c in colors if c.get("name")]
                ),
                "Attribute 2 name": "Beden",
                "Attribute 2 value(s)": ", ".join([s for s in sizes if s]),
            })

            variation_id = current_id + 1
            for color in colors:
                color_name = color.get("name", "")
                color_code = color.get("code", "UNK")

                for size in sizes:
                    if not size:
                        continue

                    rows.append({
                        "ID": f"P{variation_id:04d}",
                        "Type": "variation",
                        "SKU": f"{parent_sku}-{color_code}-{size}",
                        "Name": f"{product_name} - {color_name}",
                        "Published": 1,
                        "Is featured?": 0,
                        "Visibility in catalog": "visible",
                        "Short description": product_data.get("short_description", ""),
                        "Description": "",
                        "Regular price": product_data.get("regular_price", ""),
                        "Sale price": product_data.get("sale_price", ""),
                        "Categories": "",
                        "Images": color.get("image_urls") or images,
                        "Parent": parent_sku,
                        "Position": 0,
                        "Attribute 1 name": "Renk",
                        "Attribute 1 value(s)": color_name,
                        "Attribute 2 name": "Beden",
                        "Attribute 2 value(s)": size,
                    })
                    variation_id += 1

            current_id = variation_id

        return rows

    def build_dataframe(self, rows):
        return pd.DataFrame(rows)
