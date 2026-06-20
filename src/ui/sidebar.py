"""
Sidebar bileşenleri.
"""

import json
from pathlib import Path
import streamlit as st

# Ayarların kaydedileceği dosya yolu
SETTINGS_FILE = Path("data/settings.json")

def load_settings():
    """Kayıtlı ayarları JSON dosyasından okur."""
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_settings(data):
    """Ayarları JSON dosyasına kaydeder."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def render_sidebar():
    """Sol menüyü oluşturur."""
    st.sidebar.title("Woo Product Generator")
    
    # 1. Mevcut ayarları yükle
    saved_settings = load_settings()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Ürün Modu")
    product_mode = st.sidebar.radio(
        "İşlem tipi",
        options=["Yeni ürün olarak oluştur", "Mevcut ürünü güncelle"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Genel Ayarlar")

    # 2. Input alanlarının "value" değerlerini saved_settings üzerinden besle
    settings = {
        "product_mode": product_mode,
        "brand_code": st.sidebar.text_input("Marka Kodu", value=saved_settings.get("brand_code", "KYX")).strip().upper() or "KYX",
        "product_type_code": st.sidebar.text_input("Ürün Tipi Kodu", value=saved_settings.get("product_type_code", "GEN")).strip().upper() or "GEN",
        "product_name_suffix": st.sidebar.text_input(
            "Ürün adı son eki",
            value=saved_settings.get("product_name_suffix", ""),
            placeholder="Örn: Baskılı Tişört, Seramik Kupa, Telefon Kılıfı",
            help="Boş bırakırsan ürün adının sonuna otomatik metin eklenmez.",
        ).strip(),
        "default_sizes": st.sidebar.multiselect(
            "Varsayılan varyasyon / beden",
            options=["XS", "S", "M", "L", "XL", "XXL", "Standart"],
            default=saved_settings.get("default_sizes", ["S", "M", "L", "XL"]),
        ),
    }

    st.sidebar.markdown("---")
    st.sidebar.subheader("FTP / Görsel Yükleme")

    settings.update({
        "use_ftp_upload": st.sidebar.checkbox(
            "Görselleri otomatik FTP'ye yükle",
            value=saved_settings.get("use_ftp_upload", True),
        ),
        "ftp_use_tls": st.sidebar.checkbox("FTPS kullan", value=saved_settings.get("ftp_use_tls", True)),
        "ftp_host": st.sidebar.text_input("FTP Host", value=saved_settings.get("ftp_host", ""), placeholder="ftp.siteadi.com"),
        "ftp_port": st.sidebar.number_input("FTP Port", min_value=1, max_value=65535, value=saved_settings.get("ftp_port", 21)),
        "ftp_username": st.sidebar.text_input("FTP Kullanıcı adı", value=saved_settings.get("ftp_username", "")),
        "ftp_password": st.sidebar.text_input("FTP Şifre", value=saved_settings.get("ftp_password", ""), type="password"),
        "ftp_remote_dir": st.sidebar.text_input(
            "Remote klasör",
            value=saved_settings.get("ftp_remote_dir", "public_html/wp-content/uploads/products"),
        ),
        "public_base_url": st.sidebar.text_input(
            "Public base URL",
            value=saved_settings.get("public_base_url", "https://siteadi.com"),
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
            value=saved_settings.get("woo_site_url", ""),
            placeholder="https://siteadi.com",
        ).strip(),
        "woo_consumer_key": st.sidebar.text_input(
            "Consumer Key",
            value=saved_settings.get("woo_consumer_key", ""),
            type="password",
        ).strip(),
        "woo_consumer_secret": st.sidebar.text_input(
            "Consumer Secret",
            value=saved_settings.get("woo_consumer_secret", ""),
            type="password",
        ).strip(),
    })

    settings["fetch_woocommerce_clicked"] = st.sidebar.button(
        "Site Bilgilerini Çek",
        use_container_width=True,
    )

    st.sidebar.markdown("---")
    
    # 3. Beni Hatırla Butonu ve Kaydetme İşlemi
    remember_me = st.sidebar.checkbox("💾 Bilgilerimi Hatırla (FTP & API)", value=saved_settings.get("remember_me", False))
    
    if remember_me:
        # Checkbox işaretliyse güncel verileri kaydet
        data_to_save = {
            "remember_me": True,
            "brand_code": settings["brand_code"],
            "product_type_code": settings["product_type_code"],
            "product_name_suffix": settings["product_name_suffix"],
            "default_sizes": settings["default_sizes"],
            "use_ftp_upload": settings["use_ftp_upload"],
            "ftp_use_tls": settings["ftp_use_tls"],
            "ftp_host": settings["ftp_host"],
            "ftp_port": settings["ftp_port"],
            "ftp_username": settings["ftp_username"],
            "ftp_password": settings["ftp_password"],
            "ftp_remote_dir": settings["ftp_remote_dir"],
            "public_base_url": settings["public_base_url"],
            "woo_site_url": settings["woo_site_url"],
            "woo_consumer_key": settings["woo_consumer_key"],
            "woo_consumer_secret": settings["woo_consumer_secret"]
        }
        save_settings(data_to_save)
    else:
        # Checkbox kaldırılırsa dosyayı temizle (sadece false bilgisini tut)
        save_settings({"remember_me": False})

    settings["reset_counter_and_cache_clicked"] = st.sidebar.button(
        "Sayacı ve Hafızayı Sıfırla",
        use_container_width=True,
    )

    st.sidebar.caption("WooCommerce Product Manager")

    return settings
