"""
CSV yardımcı işlemleri
"""

import pandas as pd
from pathlib import Path


def export_dataframe_to_csv(df: pd.DataFrame, output_path: str):
    """
    DataFrame'i CSV olarak kaydeder.
    """
    path = Path(output_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )


def create_empty_woocommerce_dataframe():
    """
    WooCommerce için temel kolonları oluşturur.
    """

    columns = [
        "ID",
        "Type",
        "SKU",
        "Name",
        "Published",
        "Regular price",
        "Sale price",
        "Categories",
        "Description",
        "Short description",
        "Images",
        "Parent",
        "Position",
        "Attribute 1 name",
        "Attribute 1 value(s)",
        "Attribute 1 visible",
        "Attribute 1 global",
        "Attribute 2 name",
        "Attribute 2 value(s)",
        "Attribute 2 visible",
        "Attribute 2 global",
    ]

    return pd.DataFrame(columns=columns)
