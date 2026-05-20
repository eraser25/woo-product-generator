"""
WooCommerce API ayarları ve dinamik attribute seçimleri.
"""

from __future__ import annotations

import streamlit as st


COMMON_ATTRIBUTES = [
    {"id": None, "name": "Renk", "slug": "pa_renk", "terms": []},
    {"id": None, "name": "Beden", "slug": "pa_beden", "terms": []},
    {"id": None, "name": "Ayak Numarası", "slug": "pa_ayak-numarasi", "terms": []},
    {"id": None, "name": "Yaka Tipi", "slug": "pa_yaka-tipi", "terms": []},
]


def _names(items):
    return [str(item.get("name", "")) for item in items if item.get("name")]


def render_woocommerce_section(site_data: dict | None):
    """WooCommerce verileriyle kategori, marka ve attribute seçimlerini çizer."""
    st.header("WooCommerce Ayarları")

    site_data = site_data or {}
    categories = site_data.get("categories", [])
    brands = site_data.get("brands", [])
    attributes = site_data.get("attributes", [])

    col1, col2 = st.columns(2)

    category_names = _names(categories)
    brand_names = _names(brands)

    with col1:
        selected_category = st.selectbox(
            "Kategori",
            options=[""] + category_names,
            index=0,
        )

    with col2:
        selected_brand = st.selectbox(
            "Marka",
            options=[""] + brand_names,
            index=0,
        )

    available_attributes = attributes or COMMON_ATTRIBUTES
    attribute_names = _names(available_attributes)

    selected_attribute_names = st.multiselect(
        "Varyasyon Attribute'ları",
        options=attribute_names,
        default=[name for name in ["Renk", "Beden"] if name in attribute_names],
    )

    selected_attributes = []
    for attr_name in selected_attribute_names:
        attr = next((item for item in available_attributes if item.get("name") == attr_name), None)
        if not attr:
            continue

        term_names = _names(attr.get("terms", []))
        values = st.multiselect(
            f"{attr_name} değerleri",
            options=term_names,
            default=term_names[: min(len(term_names), 4)] if term_names else [],
            key=f"attr_values_{attr_name}",
        )

        manual_values = st.text_input(
            f"{attr_name} manuel değerler",
            placeholder="Virgülle ayır: S,M,L veya 38,39,40",
            key=f"attr_manual_{attr_name}",
        )
        if manual_values.strip():
            values = [item.strip() for item in manual_values.split(",") if item.strip()]

        selected_attributes.append({
            "id": attr.get("id"),
            "name": attr_name,
            "slug": attr.get("slug", ""),
            "values": values,
            "global": 1,
        })

    return {
        "category": selected_category,
        "brand": selected_brand,
        "attributes": selected_attributes,
    }
