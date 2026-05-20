"""
Toplu ürün bilgileri formu.
"""

import streamlit as st


def render_product_form(woocommerce_selection: dict | None = None):
    """Ortak ürün bilgileri alanı."""
    woocommerce_selection = woocommerce_selection or {}

    st.header("Toplu Ürün Bilgileri")

    col1, col2 = st.columns(2)

    with col1:
        regular_price = st.number_input("Normal Fiyat", min_value=0.0, value=399.90)
        sale_price = st.number_input("İndirimli Fiyat", min_value=0.0, value=0.0)
        stock = st.number_input("Stok", min_value=0, value=100)

    with col2:
        category = st.text_input(
            "Kategori",
            value=woocommerce_selection.get("category") or "Ürünler",
        )
        brand = st.text_input(
            "Marka",
            value=woocommerce_selection.get("brand") or "",
        )
        short_description = st.text_area(
            "Kısa Açıklama",
            value="",
            placeholder="Ürün listesinde görünecek kısa açıklama",
        )

    description = st.text_area(
        "Detaylı Açıklama",
        value="",
        placeholder="Ürün açıklaması",
    )

    image_urls = st.text_area(
        "Manuel görsel URL'leri",
        placeholder="https://site.com/1.jpg,https://site.com/2.jpg",
    )

    return {
        "regular_price": regular_price,
        "sale_price": sale_price,
        "stock": stock,
        "category": category,
        "brand": brand,
        "short_description": short_description,
        "description": description,
        "image_urls": image_urls,
    }
