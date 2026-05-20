"""
Woo Product Generator
Ana uygulama giriş noktası.
"""

import json
import os
import re
from pathlib import Path

import streamlit as st

from app_license.license_screen import render_license_gate
from src.exporters.woocommerce_csv import WooCommerceCSVExporter
from src.services.ftp_service import FTPImageUploader
from src.services.image_cache import ImageCache
from src.services.import_service import ImportService
from src.services.preview_service import PreviewService
from src.services.woocommerce_api import WooCommerceAPIClient
from src.ui.export_section import render_export_section
from src.ui.mapping_section import render_mapping_section
from src.ui.preview_table import render_preview_table
from src.ui.product_form import render_product_form
from src.ui.sidebar import render_sidebar
from src.ui.upload_section import render_upload_section
from src.ui.woocommerce_section import render_woocommerce_section


st.set_page_config(page_title="Woo Product Generator", layout="wide")

APPDATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
LICENSE_DIR = APPDATA_DIR / "Woo Product Generator" / "license"
LICENSE_DIR.mkdir(parents=True, exist_ok=True)

license_ok = render_license_gate(
    public_key_path="data/license/public_key.pem",
    license_path=str(LICENSE_DIR / "license.json"),
    support_email="destek@keepyourx.com",
    whatsapp_url="https://wa.me/905000000000",
    website_url="https://keepyourx.com",
)

if not license_ok:
    st.stop()


st.title("Woo Product Generator")

COUNTER_FILE = Path("data/uploads/counter.json")
IMAGE_CACHE_FILE = Path("data/uploads/image_cache.json")


def load_next_id() -> int:
    if COUNTER_FILE.exists():
        try:
            data = json.loads(COUNTER_FILE.read_text(encoding="utf-8"))
            return int(data.get("next_id", 1))
        except Exception:
            return 1
    return 1


def save_next_id(next_id: int) -> None:
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    COUNTER_FILE.write_text(
        json.dumps({"next_id": next_id}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def extract_next_id_from_dataframe(df) -> int:
    """DataFrame içindeki ID sütunundan sonraki ID'yi bulur."""
    if df is None or df.empty or "ID" not in df.columns:
        return st.session_state.next_id

    max_id = 0
    for value in df["ID"].tolist():
        if value is None:
            continue

        match = re.search(r"(\d+)$", str(value).strip())
        if match:
            max_id = max(max_id, int(match.group(1)))

    return max_id + 1 if max_id > 0 else st.session_state.next_id


def build_image_cache() -> ImageCache:
    return ImageCache(IMAGE_CACHE_FILE)


def build_ftp_uploader(settings: dict) -> FTPImageUploader:
    return FTPImageUploader(
        host=settings["ftp_host"],
        username=settings["ftp_username"],
        password=settings["ftp_password"],
        port=int(settings["ftp_port"]),
        public_base_url=settings["public_base_url"],
        use_tls=bool(settings.get("ftp_use_tls", True)),
        image_cache=build_image_cache(),
    )


def has_required_ftp_settings(settings: dict) -> bool:
    required = [
        settings.get("ftp_host", "").strip(),
        settings.get("ftp_username", "").strip(),
        settings.get("ftp_password", "").strip(),
        settings.get("ftp_remote_dir", "").strip(),
        settings.get("public_base_url", "").strip(),
    ]
    return all(required)


def has_required_woo_settings(settings: dict) -> bool:
    required = [
        settings.get("woo_site_url", "").strip(),
        settings.get("woo_consumer_key", "").strip(),
        settings.get("woo_consumer_secret", "").strip(),
    ]
    return all(required)


def build_woo_client(settings: dict) -> WooCommerceAPIClient:
    return WooCommerceAPIClient(
        site_url=settings["woo_site_url"],
        consumer_key=settings["woo_consumer_key"],
        consumer_secret=settings["woo_consumer_secret"],
    )


if "next_id" not in st.session_state:
    st.session_state.next_id = load_next_id()

if "generated_df" not in st.session_state:
    st.session_state.generated_df = None

if "generated_csv" not in st.session_state:
    st.session_state.generated_csv = ""

if "output_path" not in st.session_state:
    st.session_state.output_path = ""

if "woocommerce_site_data" not in st.session_state:
    st.session_state.woocommerce_site_data = {}


settings = render_sidebar()

if settings.get("reset_counter_and_cache_clicked"):
    st.session_state.next_id = 1
    save_next_id(1)
    build_image_cache().clear()
    st.sidebar.success("Sayaç ve görsel hafızası sıfırlandı.")

if settings.get("test_ftp_connection_clicked"):
    if not has_required_ftp_settings(settings):
        st.sidebar.warning("Test için tüm FTP alanlarını doldurmalısın.")
    else:
        try:
            with st.sidebar:
                with st.spinner("FTP bağlantısı test ediliyor..."):
                    result = build_ftp_uploader(settings).test_connection(settings["ftp_remote_dir"])
            st.sidebar.success("FTP bağlantısı, yazma izni ve URL yapısı başarılı.")
            st.sidebar.caption(f"Örnek URL: {result['public_url']}")
        except Exception as exc:
            st.sidebar.error(f"FTP bağlantısı başarısız: {exc}")

if settings.get("fetch_woocommerce_clicked"):
    if not has_required_woo_settings(settings):
        st.sidebar.warning("Site URL, Consumer Key ve Consumer Secret alanlarını doldurmalısın.")
    else:
        try:
            with st.sidebar:
                with st.spinner("WooCommerce bilgileri çekiliyor..."):
                    site_data = build_woo_client(settings).fetch_site_data()
            st.session_state.woocommerce_site_data = {
                "categories": site_data.categories,
                "attributes": site_data.attributes,
                "brands": site_data.brands,
            }
            st.sidebar.success("Site bilgileri çekildi.")
        except Exception as exc:
            st.sidebar.error(f"WooCommerce API hatası: {exc}")


woocommerce_selection = render_woocommerce_section(st.session_state.woocommerce_site_data)

import_service = ImportService()
preview_service = PreviewService()
exporter = WooCommerceCSVExporter()

uploaded_files = render_upload_section()
products = import_service.process_uploaded_files(uploaded_files)
mapping_result = render_mapping_section(
    products,
    product_name_suffix=settings["product_name_suffix"],
    product_mode=settings["product_mode"],
)
product_data = render_product_form(woocommerce_selection)

st.divider()

generate_clicked = st.button("CSV Oluştur", use_container_width=True)

active_attributes = woocommerce_selection.get("attributes", [])

if generate_clicked:
    if not mapping_result:
        st.warning("Önce ürün yüklemelisin.")
    elif not active_attributes and not settings["default_sizes"]:
        st.warning("En az bir attribute değeri veya varsayılan varyasyon seçmelisin.")
    else:
        if settings.get("use_ftp_upload"):
            if has_required_ftp_settings(settings):
                try:
                    with st.spinner("Görseller FTP'ye yükleniyor..."):
                        mapping_result = build_ftp_uploader(settings).upload_mapping_images(
                            mapping_result=mapping_result,
                            remote_base_dir=settings["ftp_remote_dir"],
                        )

                    st.success("Görseller FTP'ye yüklendi ve hafızaya işlendi.")
                except Exception as exc:
                    st.error(f"FTP yükleme hatası: {exc}")
                    st.stop()
            else:
                st.warning(
                    "FTP yükleme açık fakat bazı alanlar boş. "
                    "CSV manuel URL alanlarıyla devam edecek."
                )

        csv_dataframe = exporter.build_rows(
            mappings=mapping_result,
            product_data=product_data,
            sizes=settings["default_sizes"],
            brand_code=settings["brand_code"],
            product_type_code=settings["product_type_code"],
            start_id=st.session_state.next_id,
            product_name_suffix=settings["product_name_suffix"],
            attributes=active_attributes,
            product_mode=settings["product_mode"],
        )

        csv_string = exporter.export_csv_string(csv_dataframe)

        output_dir = Path("data/uploads/csv")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "woocommerce_products.csv"

        exporter.export_csv_file(csv_dataframe, str(output_path))

        st.session_state.generated_df = csv_dataframe
        st.session_state.generated_csv = csv_string
        st.session_state.output_path = str(output_path)

        if settings["product_mode"] == "Yeni ürün olarak oluştur":
            st.session_state.next_id = extract_next_id_from_dataframe(csv_dataframe)
            save_next_id(st.session_state.next_id)

        st.success("CSV oluşturuldu ve kaydedildi.")

preview_rows = []
if mapping_result:
    preview_rows = preview_service.build_preview_rows(
        mappings=mapping_result,
        product_data=product_data,
        sizes=settings["default_sizes"],
        brand_code=settings["brand_code"],
        product_type_code=settings["product_type_code"],
        start_id=st.session_state.next_id,
    )

render_preview_table(preview_rows)
render_export_section(st.session_state.generated_csv)

if st.session_state.output_path:
    st.caption(f"Son CSV yolu: {st.session_state.output_path}")

with st.expander("Oluşturulan CSV'yi tablo olarak göster"):
    if st.session_state.generated_df is not None:
        st.dataframe(st.session_state.generated_df, use_container_width=True, height=500)
    else:
        st.write("Henüz veri yok.")
