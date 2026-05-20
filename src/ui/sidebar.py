"""
Sidebar bileşenleri.
"""

import streamlit as st


def render_sidebar():
    """Sol menüyü oluşturur."""
    st.sidebar.title("Woo Product Generator")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Ürün Modu")
    product_mode = st.sidebar.radio(
        "İşlem tipi",
        options=["Yeni ürün olarak oluştur", "Mevcut ürünü güncelle"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Genel Ayarlar")

    settings = {
        "product_mode": product_mode,
        "brand_code": st.sidebar.text_input("Marka Kodu", value="KYX").strip().upper() or "KYX",
        "product_type_code": st.sidebar.text_input("Ürün Tipi Kodu", value="GEN").strip().upper() or "GEN",
        "product_name_suffix": st.sidebar.text_input(
            "Ürün adı son eki",
            value="",
            placeholder="Örn: Baskılı Tişört, Seramik Kupa, Telefon Kılıfı",
            help="Boş bırakırsan ürün adının sonuna otomatik metin eklenmez.",
        ).strip(),
        "default_sizes": st.sidebar.multiselect(
            "Varsayılan varyasyon / beden",
            options=["XS", "S", "M", "L", "XL", "XXL", "Standart"],
            default=["S", "M", "L", "XL"],
        ),
    }

    st.sidebar.markdown("---")
    st.sidebar.subheader("FTP / Görsel Yükleme")

    settings.update({
        "use_ftp_upload": st.sidebar.checkbox(
            "Görselleri otomatik FTP'ye yükle",
            value=True,
        ),
        "ftp_use_tls": st.sidebar.checkbox("FTPS kullan", value=True),
        "ftp_host": st.sidebar.text_input("FTP Host", value="", placeholder="ftp.siteadi.com"),
        "ftp_port": st.sidebar.number_input("FTP Port", min_value=1, max_value=65535, value=21),
        "ftp_username": st.sidebar.text_input("FTP Kullanıcı adı", value=""),
        "ftp_password": st.sidebar.text_input("FTP Şifre", value="", type="password"),
        "ftp_remote_dir": st.sidebar.text_input(
            "Remote klasör",
            value="public_html/wp-content/uploads/products",
        ),
        "public_base_url": st.sidebar.text_input(
            "Public base URL",
            value="https://siteadi.com",
        ),
    })

    settings["test_ftp_connection_clicked"] = st.sidebar.button(
        "FTP Bağlantısını Test Et",
        use_container_width=True,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("WooCommerce REST API")

    settings.update({
        "woo_site_url": st.sidebar.text_input(
            "Site URL",
            value="",
            placeholder="https://siteadi.com",
        ).strip(),
        "woo_consumer_key": st.sidebar.text_input(
            "Consumer Key",
            value="",
            type="password",
        ).strip(),
        "woo_consumer_secret": st.sidebar.text_input(
            "Consumer Secret",
            value="",
            type="password",
        ).strip(),
    })

    settings["fetch_woocommerce_clicked"] = st.sidebar.button(
        "Site Bilgilerini Çek",
        use_container_width=True,
    )

    st.sidebar.markdown("---")
    settings["reset_counter_and_cache_clicked"] = st.sidebar.button(
        "Sayacı ve Hafızayı Sıfırla",
        use_container_width=True,
    )

    st.sidebar.caption("WooCommerce Product Manager")

    return settings
