"""
Streamlit lisans giriş ekranı.
"""

from __future__ import annotations

import streamlit as st

from .license_manager import OfflineLicenseManager


def render_purchase_box(
    support_email: str = "info@siteadi.com",
    whatsapp_url: str = "https://wa.me/905xxxxxxxxx",
    website_url: str = "https://siteadi.com",
) -> None:
    st.markdown("### Satın Alma")
    st.write("Lisans süreniz dolduysa yeni anahtar almak için aşağıdaki kanalları kullanın.")
    st.link_button("Web Sitesi", website_url)
    st.link_button("WhatsApp", whatsapp_url)
    st.write(f"Email: {support_email}")


def render_license_gate(
    public_key_path: str = "data/license/public_key.pem",
    license_path: str = "data/license/license.json",
    support_email: str = "info@siteadi.com",
    whatsapp_url: str = "https://wa.me/905xxxxxxxxx",
    website_url: str = "https://siteadi.com",
    title: str = "Lisans Etkinleştirme",
) -> bool:
    """Lisans aktifse True döner, değilse lisans ekranını gösterir."""
    manager = OfflineLicenseManager(
        public_key_path=public_key_path,
        license_path=license_path,
    )

    check = manager.check_local_license()

    if check.active:
        st.success("Lisans aktif.")
        if check.payload:
            st.caption(f"Plan: {check.payload.get('plan_name', '-')}")
            st.caption(f"Bitiş tarihi: {check.payload.get('expires_at', '-')}")
            days = manager.days_left()
            if days is not None:
                st.caption(f"Kalan gün: {days}")
        with st.expander("Lisansı kaldır"):
            if st.button("Bu cihazdaki lisansı sil"):
                manager.deactivate()
                st.rerun()
        return True

    st.warning("Uygulama kullanıma kapalı.")
    st.subheader(title)
    st.write("Devam etmek için lisans anahtarını gir.")

    license_key = st.text_area(
        "Lisans Anahtarı",
        placeholder="KYX1....",
        height=140,
    )

    col1, col2 = st.columns(2)

    with col1:
        activate_clicked = st.button("Lisansı Aktive Et", use_container_width=True)

    with col2:
        purchase_clicked = st.button("Satın Al", use_container_width=True)

    if activate_clicked:
        if not license_key.strip():
            st.error("Lisans anahtarı boş olamaz.")
        else:
            result = manager.activate(license_key)
            if result.active:
                st.success("Lisans başarıyla aktive edildi.")
                st.rerun()
            else:
                st.error(result.reason)

    if purchase_clicked:
        render_purchase_box(
            support_email=support_email,
            whatsapp_url=whatsapp_url,
            website_url=website_url,
        )

    with st.expander("Lisans bilgileri"):
        st.write("Bu sürüm sunucusuz çalışır.")
        st.write("Aktivasyon bilgisayar bazında yerelde saklanır.")
        st.write("Süre dolunca uygulama bu ekrandan devam eder.")

    return False
