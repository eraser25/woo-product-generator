"""
Dosya yükleme alanı.
"""

import streamlit as st


def render_upload_section():
    """Görsel yükleme alanı."""
    st.header("Ürün Görselleri")

    return st.file_uploader(
        "Ürün görsellerini yükle",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )
