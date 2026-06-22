"""
FTP/FTPS ile görsel yükleme servisi.
"""

from __future__ import annotations

import streamlit as st
import hashlib
import io
import re
from ftplib import FTP, FTP_TLS, error_perm
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from src.services.image_cache import ImageCache
from src.utils.text_utils import ascii_key


class FTPImageUploader:
    """Görselleri FTP sunucusuna yükler ve public URL üretir."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 21,
        timeout: int = 30,
        public_base_url: str = "",
        use_tls: bool = True,
        image_cache: ImageCache | None = None,
    ) -> None:
        self.host = host.strip()
        self.username = username.strip()
        self.password = password
        self.port = int(port)
        self.timeout = timeout
        self.public_base_url = public_base_url.rstrip("/")
        self.use_tls = bool(use_tls)
        self.image_cache = image_cache or ImageCache()

    def _connect(self):
        ftp = FTP_TLS() if self.use_tls else FTP()
        ftp.connect(self.host, self.port, timeout=self.timeout)
        ftp.login(self.username, self.password)
        if self.use_tls:
            ftp.prot_p()
        ftp.set_pasv(True)
        return ftp

    def test_connection(self, remote_dir: str = "") -> Dict[str, Any]:
        """Bağlantı, klasör yazma izni ve public URL yapısını kontrol eder."""
        parsed = urlparse(self.public_base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(
                "Public base URL http veya https ile başlayan geçerli bir URL olmalı."
            )

        ftp = self._connect()
        test_filename = f"woo-product-generator-test-{hashlib.sha1(self.username.encode()).hexdigest()[:8]}.txt"

        try:
            self._ensure_remote_dir(ftp, remote_dir)
            with io.BytesIO(b"connection-ok") as bio:
                ftp.storbinary(f"STOR {test_filename}", bio)

            try:
                ftp.delete(test_filename)
            except Exception:
                pass

            public_url = self._build_public_url(remote_dir, test_filename)
            return {
                "connected": True,
                "writable": True,
                "public_url": public_url,
            }
        finally:
            try:
                ftp.quit()
            except Exception:
                try:
                    ftp.close()
                except Exception:
                    pass

    def _safe_filename(self, filename: str, file_bytes: bytes | None = None) -> str:
        suffix = Path(filename).suffix.lower()
        stem = Path(filename).stem.strip() or "image"
        ascii_stem = ascii_key(stem)
        ascii_stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", ascii_stem).strip(".-_").lower()
        ascii_stem = ascii_stem or "image"

        if file_bytes:
            digest = hashlib.sha1(file_bytes).hexdigest()[:10]
            ascii_stem = f"{ascii_stem}-{digest}"

        return f"{ascii_stem}{suffix}"

    def _normalize_remote_dir(self, remote_dir: str) -> str:
        return remote_dir.strip().replace("\\", "/").strip("/")

    def _public_path_from_remote_dir(self, remote_dir: str) -> str:
        remote_dir_clean = self._normalize_remote_dir(remote_dir)
        if remote_dir_clean.startswith("public_html/"):
            remote_dir_clean = remote_dir_clean[len("public_html/") :]
        return remote_dir_clean.strip("/")

    def _ensure_remote_dir(self, ftp, remote_dir: str) -> None:
        remote_dir_clean = self._normalize_remote_dir(remote_dir)
        if not remote_dir_clean:
            return

        parts = [p for p in remote_dir_clean.split("/") if p]

        try:
            ftp.cwd("/")
        except Exception:
            pass

        for part in parts:
            try:
                ftp.cwd(part)
            except error_perm:
                ftp.mkd(part)
                ftp.cwd(part)

    def _build_public_url(self, remote_dir: str, filename: str) -> str:
        public_path = self._public_path_from_remote_dir(remote_dir)
        if public_path:
            return f"{self.public_base_url}/{public_path}/{filename}"
        return f"{self.public_base_url}/{filename}"

    def upload_bytes(
        self,
        file_bytes: bytes,
        remote_dir: str,
        filename: str,
    ) -> str:
        if not file_bytes:
            raise ValueError("Boş dosya verisi yüklenemez.")

        cached_url = self.image_cache.get(file_bytes)
        if cached_url:
            return cached_url

        safe_name = self._safe_filename(filename, file_bytes)
        ftp = self._connect()

        try:
            self._ensure_remote_dir(ftp, remote_dir)
            with io.BytesIO(file_bytes) as bio:
                ftp.storbinary(f"STOR {safe_name}", bio)
        finally:
            try:
                ftp.quit()
            except Exception:
                try:
                    ftp.close()
                except Exception:
                    pass

        public_url = self._build_public_url(remote_dir, safe_name)
        self.image_cache.set(file_bytes, public_url)
        return public_url

    def upload_mapping_images(
        self,
        mapping_result: Dict[str, Dict[str, Any]],
        remote_base_dir: str,
    ) -> Dict[str, Dict[str, Any]]:
        remote_base_dir_clean = self._normalize_remote_dir(remote_base_dir)

        # 1. Yüklenecek toplam görsel sayısını bul (İlerleme çubuğu için)
        total_images = 0
        for group_key, item in mapping_result.items():
            for color in item.get("colors", []):
                if color.get("image_bytes") and color.get("filename"):
                    total_images += 1

        # 2. İlerleme çubuğunu ve metin alanını oluştur
        progress_bar = st.progress(0)
        status_text = st.empty()
        uploaded_count = 0

        for group_key, item in mapping_result.items():
            group_dir = (
                f"{remote_base_dir_clean}/{group_key}"
                if remote_base_dir_clean
                else group_key
            )

            gallery_urls = []
            for color in item.get("colors", []):
                image_bytes = color.get("image_bytes")
                filename = color.get("filename", "")

                if not image_bytes or not filename:
                    if color.get("image_urls"):
                        gallery_urls.extend(
                            self._split_urls(color.get("image_urls", ""))
                        )
                    continue

                # 3. Görseli yükle
                url = self.upload_bytes(
                    file_bytes=image_bytes,
                    remote_dir=group_dir,
                    filename=filename,
                )
                color["image_urls"] = url
                gallery_urls.append(url)

                # 4. İlerleme Çubuğunu Güncelle
                uploaded_count += 1
                if total_images > 0:
                    yuzde = int((uploaded_count / total_images) * 100)
                    progress_bar.progress(yuzde)
                    status_text.caption(f"🚀 FTP'ye Yükleniyor: {filename} (%{yuzde})")

            parent_urls = self._split_urls(item.get("image_urls", ""))
            combined = self._unique_urls(parent_urls + gallery_urls)
            item["image_urls"] = ",".join(combined)
            item["main_image_url"] = combined[0] if combined else ""
            item["gallery_image_urls"] = (
                ",".join(combined[1:]) if len(combined) > 1 else ""
            )

        # 5. İşlem bitince başarılı mesajı bas, bekle ve çubuğu gizle
        if total_images > 0:
            status_text.success(
                f"✅ Toplam {total_images} görsel FTP'ye başarıyla yüklendi!"
            )
            import time

            time.sleep(2)
            progress_bar.empty()
            status_text.empty()

        return mapping_result

    def _split_urls(self, value: str) -> list[str]:
        return [item.strip() for item in str(value or "").split(",") if item.strip()]

    def _unique_urls(self, urls: list[str]) -> list[str]:
        seen = set()
        unique = []
        for url in urls:
            if url and url not in seen:
                seen.add(url)
                unique.append(url)
        return unique
