"""
Ürün eşleştirme alanı.
"""

from io import BytesIO

import streamlit as st


def _show_thumbnail(image_bytes, caption: str = "", width: int = 110):
    """Bytes olarak gelen görseli gösterir."""
    if not image_bytes:
        st.caption("Görsel yok")
        return

    try:
        st.image(BytesIO(image_bytes), caption=caption, width=width)
    except Exception:
        st.caption("Görsel önizlenemedi")


def _with_suffix(name: str, suffix: str) -> str:
    name = (name or "").strip()
    suffix = (suffix or "").strip()
    if not name or not suffix:
        return name
    if name.lower().endswith(suffix.lower()):
        return name
    return f"{name} {suffix}"


def render_mapping_section(products, product_name_suffix: str = "", product_mode: str = ""):
    """Ürün gruplarını kullanıcı onayıyla CSV mapping verisine çevirir."""
    st.header("Ürün Eşleştirme")

    if not products:
        st.info("Henüz ürün bulunamadı.")
        return {}

    mapping_result = {}

    for product in products:
        group_key = product["group_key"]
        st.subheader(product["suggested_name"])

        if product.get("colors"):
            colors_text = ", ".join([c["name"] for c in product["colors"]])
            st.caption(f"Algılanan renkler: {colors_text}")

            thumbs_cols = st.columns(min(len(product["colors"]), 4))
            for idx, color in enumerate(product["colors"][:4]):
                with thumbs_cols[idx % len(thumbs_cols)]:
                    _show_thumbnail(
                        color.get("image_bytes"),
                        caption=color.get("name", ""),
                        width=110,
                    )

        col1, col2 = st.columns([2, 2])

        with col1:
            product_name = st.text_input(
                f"Ürün Adı - {group_key}",
                value=_with_suffix(product["suggested_name"], product_name_suffix),
                key=f"name_{group_key}",
            )

        with col2:
            category = st.text_input(
                f"Kategori - {group_key}",
                value="Ürünler",
                key=f"cat_{group_key}",
            )

        existing_parent_id = ""
        existing_parent_sku = ""
        if product_mode == "Mevcut ürünü güncelle":
            update_col1, update_col2 = st.columns(2)
            with update_col1:
                existing_parent_id = st.text_input(
                    f"Mevcut Woo ID - {group_key}",
                    key=f"existing_id_{group_key}",
                )
            with update_col2:
                existing_parent_sku = st.text_input(
                    f"Mevcut SKU - {group_key}",
                    key=f"existing_sku_{group_key}",
                )

        product_image_urls = st.text_area(
            f"Genel ürün görselleri - {group_key}",
            placeholder="https://site.com/genel1.jpg,https://site.com/genel2.jpg",
            key=f"images_{group_key}",
        )

        st.markdown("**Renge göre görseller**")

        color_entries = []
        for idx, color in enumerate(product.get("colors", [])):
            color_row_1, color_row_2, color_row_3 = st.columns([1, 1, 3])

            with color_row_1:
                _show_thumbnail(
                    color.get("image_bytes"),
                    caption=color.get("name", ""),
                    width=90,
                )

            with color_row_2:
                color_name = st.text_input(
                    f"Renk adı - {group_key} - {idx}",
                    value=color.get("name", ""),
                    key=f"color_name_{group_key}_{idx}",
                )

            with color_row_3:
                color_images = st.text_area(
                    f"{color_name or 'Renk'} görsel URL'leri",
                    placeholder="https://site.com/beyaz1.jpg,https://site.com/beyaz2.jpg",
                    key=f"color_images_{group_key}_{idx}",
                )

            color_entries.append({
                "name": color_name,
                "code": color.get("code", ""),
                "filename": color.get("filename", ""),
                "image_bytes": color.get("image_bytes"),
                "image_urls": color_images,
            })

        mapping_result[group_key] = {
            "product_name": product_name,
            "category": category,
            "colors": color_entries,
            "files": product.get("files", []),
            "image_urls": product_image_urls,
            "existing_parent_id": existing_parent_id,
            "existing_parent_sku": existing_parent_sku,
        }

        st.markdown("---")

    return mapping_result
