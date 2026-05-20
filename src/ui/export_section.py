"""
CSV export alanı.
"""

import streamlit as st


def render_export_section(csv_data: str):
    """CSV indirme butonu."""
    st.header("CSV Export")

    if not csv_data:
        st.info("Henüz export edilecek veri yok.")
        return

    st.download_button(
        label="WooCommerce CSV İndir",
        data=csv_data,
        file_name="woocommerce_products.csv",
        mime="text/csv",
    )
