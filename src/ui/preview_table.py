"""
Önizleme tablosu.
"""

import pandas as pd
import streamlit as st


def render_preview_table(data):
    """CSV önizleme tablosu."""
    st.header("CSV Önizleme")

    if data is None or len(data) == 0:
        st.warning("Önizlenecek veri bulunamadı.")
        return

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True,
        height=500,
    )
