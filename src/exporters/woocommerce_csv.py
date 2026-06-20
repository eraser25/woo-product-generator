"""
WooCommerce CSV export sistemi.
"""

from itertools import product
from io import StringIO
from typing import Any, Dict, List, Union

import pandas as pd

from src.utils.text_utils import ascii_key


class WooCommerceCSVExporter:
    """WooCommerce için dinamik attribute destekli CSV satırları üretir."""

    def __init__(self) -> None:
        self.base_columns = [
            "ID",
            "Type",
            "SKU",
            "Name",
            "Published",
            "Is featured?",
            "Visibility in catalog",
            "Short description",
            "Description",
            "Date sale price starts",
            "Date sale price ends",
            "Tax status",
            "Tax class",
            "In stock?",
            "Stock",
            "Backorders allowed?",
            "Sold individually?",
            "Weight (lbs)",
            "Length (in)",
            "Width (in)",
            "Height (in)",
            "Allow customer reviews?",
            "Purchase note",
            "Sale price",
            "Regular price",
            "Categories",
            "Tags",
            "Shipping class",
            "Images",
            "Download limit",
            "Download expiry days",
            "Parent",
            "Grouped products",
            "Position",
        ]
        self.tail_columns = ["Meta: _wpcom_is_markdown"]
        self.color_code_map = {
            "beyaz": "BYZ",
            "siyah": "SYH",
            "kirmizi": "KRM",
            "mavi": "MAV",
            "yesil": "YSL",
            "gri": "GRI",
            "lacivert": "LCV",
        }

    def _columns_for_attribute_count(self, count: int) -> list[str]:
        columns = list(self.base_columns)
        for index in range(1, max(count, 1) + 1):
            columns.extend(
                [
                    f"Attribute {index} name",
                    f"Attribute {index} value(s)",
                    f"Attribute {index} visible",
                    f"Attribute {index} global",
                ]
            )
        columns.extend(self.tail_columns)
        return columns

    def _normalize_title(self, product_name: str, suffix: str = "") -> str:
        base = (product_name or "").strip()
        suffix = (suffix or "").strip()
        if not base:
            return ""
        if not suffix:
            return base
        if base.lower().endswith(suffix.lower()):
            return base
        return f"{base} {suffix}"

    def _normalize_color_code(self, color_name: str) -> str:
        key = ascii_key(color_name)
        if not key:
            return "UNK"
        return self.color_code_map.get(key, key[:3].upper())

    def _normalize_images(self, images: Union[str, List[str], None]) -> str:
        if not images:
            return ""

        if isinstance(images, list):
            cleaned = [str(x).strip() for x in images if str(x).strip()]
            return ",".join(cleaned)

        if isinstance(images, str):
            cleaned = [x.strip() for x in images.split(",") if x.strip()]
            return ",".join(cleaned)

        return ""

    def _first_image(self, images: Union[str, List[str], None]) -> str:
        normalized = self._normalize_images(images)
        if not normalized:
            return ""
        return normalized.split(",")[0].strip()

    def _combine_unique_images(self, image_list: List[str]) -> str:
        unique = []
        seen = set()

        for item in image_list:
            normalized = self._normalize_images(item)
            if not normalized:
                continue

            for url in normalized.split(","):
                url = url.strip()
                if url and url not in seen:
                    seen.add(url)
                    unique.append(url)

        return ",".join(unique)

    def _normalize_price(self, value: Any) -> Any:
        if value is None:
            return ""
        try:
            numeric = float(value)
            if numeric <= 0:
                return ""
            if numeric.is_integer():
                return int(numeric)
            return numeric
        except Exception:
            return value

    def _safe_int(self, value: Any, default: int = 0) -> int:
        try:
            return int(float(value))
        except Exception:
            return default

    def _default_attributes(self, sizes: List[str], colors: List[dict]) -> list[dict]:
        attrs = []
        # Birden fazla görsel (ön/arka) aynı renk olduğu için listeyi tekilleştiriyoruz
        color_values = list(
            dict.fromkeys([c.get("name", "") for c in colors if c.get("name")])
        )

        if color_values:
            attrs.append({"name": "Renk", "values": color_values, "global": 1})
        size_values = [str(size).strip() for size in sizes if str(size).strip()]
        if size_values:
            attrs.append({"name": "Beden", "values": size_values, "global": 1})
        return attrs

    def _clean_attributes(self, attributes: List[dict]) -> list[dict]:
        cleaned = []
        for attr in attributes or []:
            name = str(attr.get("name", "")).strip()
            values = [
                str(value).strip()
                for value in attr.get("values", [])
                if str(value).strip()
            ]
            if name and values:
                cleaned.append(
                    {
                        "name": name,
                        "values": values,
                        "global": int(attr.get("global", 1)),
                    }
                )
        return cleaned

    def _color_image_lookup(self, colors: list[dict]) -> dict:
        lookup = {}
        for color in colors:
            name = str(color.get("name", "")).strip()
            if name:
                key = ascii_key(name)
                existing_urls = lookup.get(key, "")
                new_urls = self._normalize_images(color.get("image_urls", ""))

                if new_urls:
                    if existing_urls:
                        # Arka/galeri görselini önceki URL'nin sonuna virgülle ekle
                        lookup[key] = existing_urls + "," + new_urls
                    else:
                        # İlk kez (Ana görsel) ekleniyorsa doğrudan ata
                        lookup[key] = new_urls
        return lookup

    def _variation_image(
        self,
        combination: tuple[str, ...],
        attributes: list[dict],
        color_lookup: dict,
        parent_images: str,
    ) -> str:
        for attr, value in zip(attributes, combination):
            if ascii_key(attr.get("name", "")) == "renk":
                image = color_lookup.get(ascii_key(value))
                if image:
                    return image
        return self._first_image(parent_images)

    def _sku_part(self, value: str, attr_name: str = "") -> str:
        key = ascii_key(value).replace("-", "")
        if ascii_key(attr_name) == "renk":
            return self.color_code_map.get(ascii_key(value), key[:3].upper() or "UNK")
        return key.upper()[:12] or "VAR"

    def build_rows(
        self,
        mappings: Dict[str, Dict],
        product_data: Dict[str, Any],
        sizes: List[str],
        brand_code: str = "KYX",
        product_type_code: str = "TS",
        start_id: int = 1,
        product_name_suffix: str = "",
        attributes: List[dict] | None = None,
        product_mode: str = "Yeni ürün olarak oluştur",
    ) -> pd.DataFrame:
        rows = []
        current_id = start_id

        for _, item in mappings.items():
            raw_name = item.get("product_name", "")
            product_name = self._normalize_title(raw_name, product_name_suffix)
            category = item.get("category", product_data.get("category", ""))
            brand = str(product_data.get("brand", "")).strip()
            colors = item.get("colors", []) or []

            active_attributes = self._clean_attributes(attributes or [])
            if not active_attributes:
                active_attributes = self._default_attributes(sizes, colors)
            if not active_attributes:
                continue

            update_mode = product_mode == "Mevcut ürünü güncelle"
            existing_parent_id = str(item.get("existing_parent_id", "")).strip()
            existing_parent_sku = str(item.get("existing_parent_sku", "")).strip()

            parent_id = (
                existing_parent_id
                if update_mode and existing_parent_id
                else f"P{current_id:04d}"
            )
            parent_sku = (
                existing_parent_sku
                if update_mode and existing_parent_sku
                else f"{brand_code}-{product_type_code}-{current_id:04d}"
            )

            parent_images = self._normalize_images(item.get("image_urls", ""))
            if not parent_images:
                parent_images = self._combine_unique_images(
                    [c.get("image_urls", "") for c in colors]
                )
            if product_data.get("image_urls"):
                parent_images = self._combine_unique_images(
                    [parent_images, product_data.get("image_urls", "")]
                )

            tags = brand if brand else ""

            parent_row = {
                "ID": parent_id,
                "Type": "variable",
                "SKU": parent_sku,
                "Name": product_name,
                "Published": 1,
                "Is featured?": 1,
                "Visibility in catalog": "visible",
                "Short description": product_data.get("short_description", ""),
                "Description": product_data.get("description", ""),
                "Date sale price starts": "",
                "Date sale price ends": "",
                "Tax status": "taxable",
                "Tax class": "",
                "In stock?": 1,
                "Stock": "",
                "Backorders allowed?": 0,
                "Sold individually?": 0,
                "Weight (lbs)": "",
                "Length (in)": "",
                "Width (in)": "",
                "Height (in)": "",
                "Allow customer reviews?": 1,
                "Purchase note": "",
                "Sale price": "",
                "Regular price": self._normalize_price(
                    product_data.get("regular_price", "")
                ),
                "Categories": category,
                "Tags": tags,
                "Shipping class": "",
                "Images": parent_images,
                "Download limit": "",
                "Download expiry days": "",
                "Parent": "",
                "Grouped products": "",
                "Position": 0,
                "Meta: _wpcom_is_markdown": 1,
            }

            for index, attr in enumerate(active_attributes, start=1):
                parent_row[f"Attribute {index} name"] = attr["name"]
                parent_row[f"Attribute {index} value(s)"] = ", ".join(attr["values"])
                parent_row[f"Attribute {index} visible"] = 1
                parent_row[f"Attribute {index} global"] = attr["global"]

            rows.append(parent_row)

            color_lookup = self._color_image_lookup(colors)
            combinations = list(
                product(*[attr["values"] for attr in active_attributes])
            )
            current_variation_id = current_id + 1

            for combination in combinations:
                sku_suffix = "-".join(
                    self._sku_part(value, attr["name"])
                    for attr, value in zip(active_attributes, combination)
                )
                variation_id = "" if update_mode else f"P{current_variation_id:04d}"
                variation_sku = f"{parent_sku}-{sku_suffix}"
                variation_name = f"{product_name} - {' / '.join(combination)}"

                row = {
                    "ID": variation_id,
                    "Type": "variation",
                    "SKU": variation_sku,
                    "Name": variation_name,
                    "Published": 1,
                    "Is featured?": 0,
                    "Visibility in catalog": "visible",
                    "Short description": product_data.get("short_description", ""),
                    "Description": "",
                    "Date sale price starts": "",
                    "Date sale price ends": "",
                    "Tax status": "taxable",
                    "Tax class": "",
                    "In stock?": 1,
                    "Stock": self._safe_int(product_data.get("stock", 0), 0),
                    "Backorders allowed?": 0,
                    "Sold individually?": 0,
                    "Weight (lbs)": "",
                    "Length (in)": "",
                    "Width (in)": "",
                    "Height (in)": "",
                    "Allow customer reviews?": 0,
                    "Purchase note": "",
                    "Sale price": self._normalize_price(
                        product_data.get("sale_price", "")
                    ),
                    "Regular price": self._normalize_price(
                        product_data.get("regular_price", "")
                    ),
                    "Categories": "",
                    "Tags": "",
                    "Shipping class": "",
                    "Images": self._variation_image(
                        combination, active_attributes, color_lookup, parent_images
                    ),
                    "Download limit": "",
                    "Download expiry days": "",
                    "Parent": parent_sku,
                    "Grouped products": "",
                    "Position": 0,
                    "Meta: _wpcom_is_markdown": "",
                }

                for index, (attr, value) in enumerate(
                    zip(active_attributes, combination), start=1
                ):
                    row[f"Attribute {index} name"] = attr["name"]
                    row[f"Attribute {index} value(s)"] = value
                    row[f"Attribute {index} visible"] = ""
                    row[f"Attribute {index} global"] = attr["global"]

                rows.append(row)
                current_variation_id += 1

            current_id = current_variation_id

        columns = self._columns_for_attribute_count(
            max(
                [len(self._clean_attributes(attributes or []))]
                + [len(row.keys()) for row in []]
            )
        )
        if rows:
            attr_count = max(
                len(
                    [
                        key
                        for key in row
                        if key.startswith("Attribute ") and key.endswith(" name")
                    ]
                )
                for row in rows
            )
            columns = self._columns_for_attribute_count(attr_count)

        df = pd.DataFrame(rows)
        for col in columns:
            if col not in df.columns:
                df[col] = ""

        return df[columns]

    def build_dataframe(self, rows):
        if isinstance(rows, pd.DataFrame):
            return rows
        return pd.DataFrame(rows)

    def export_csv_string(self, dataframe: pd.DataFrame) -> str:
        csv_buffer = StringIO()
        dataframe.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        return csv_buffer.getvalue()

    def export_csv_file(self, dataframe: pd.DataFrame, output_path: str) -> None:
        dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")
