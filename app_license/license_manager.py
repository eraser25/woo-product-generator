"""
Sunucusuz lisans doğrulama ve yerel aktivasyon yönetimi.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .machine_id import get_machine_fingerprint


def _b64url_decode(data: str) -> bytes:
    data = data.strip()
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass
class LicenseCheckResult:
    active: bool
    reason: str
    payload: Optional[Dict[str, Any]] = None


class OfflineLicenseManager:
    """Offline lisans yöneticisi."""

    def __init__(
        self,
        public_key_path: str | Path = "data/license/public_key.pem",
        license_path: str | Path = "data/license/license.json",
    ) -> None:
        self.public_key_path = Path(public_key_path)
        self.license_path = Path(license_path)

    def _load_public_key(self) -> Ed25519PublicKey:
        if not self.public_key_path.exists():
            raise FileNotFoundError(f"Public key bulunamadı: {self.public_key_path}")

        pem = self.public_key_path.read_bytes()
        return serialization.load_pem_public_key(pem)

    def _verify_token(self, token: str) -> Dict[str, Any]:
        parts = token.strip().split(".")
        if len(parts) != 3:
            raise ValueError("Lisans anahtarı formatı geçersiz.")

        prefix, payload_b64, signature_b64 = parts
        if prefix != "KYX1":
            raise ValueError("Lisans anahtarı ön eki geçersiz.")

        payload_bytes = _b64url_decode(payload_b64)
        signature = _b64url_decode(signature_b64)

        payload = json.loads(payload_bytes.decode("utf-8"))
        public_key = self._load_public_key()

        try:
            public_key.verify(signature, payload_bytes)
        except InvalidSignature as exc:
            raise ValueError("Lisans imzası geçersiz.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Lisans verisi geçersiz.")

        if "expires_at" not in payload:
            raise ValueError("Lisans süresi bulunamadı.")

        return payload

    def _save_local_license(self, record: Dict[str, Any]) -> None:
        self.license_path.parent.mkdir(parents=True, exist_ok=True)
        self.license_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_local_license(self) -> Optional[Dict[str, Any]]:
        if not self.license_path.exists():
            return None

        try:
            return json.loads(self.license_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def activate(self, token: str) -> LicenseCheckResult:
        try:
            payload = self._verify_token(token)
        except Exception as exc:
            return LicenseCheckResult(False, str(exc), None)

        try:
            expires_at = _parse_dt(str(payload["expires_at"]))
        except Exception:
            return LicenseCheckResult(False, "Bitiş tarihi okunamadı.", None)

        now = _utc_now()
        if expires_at <= now:
            return LicenseCheckResult(False, "Lisans süresi dolmuş.", payload)

        record = {
            "token": token.strip(),
            "payload": payload,
            "machine_fingerprint": get_machine_fingerprint(),
            "activated_at": now.isoformat(),
            "last_verified_at": now.isoformat(),
        }
        self._save_local_license(record)

        return LicenseCheckResult(True, "Lisans etkinleştirildi.", payload)

    def check_local_license(self) -> LicenseCheckResult:
        record = self._load_local_license()
        if not record:
            return LicenseCheckResult(False, "Aktif lisans bulunamadı.", None)

        token = str(record.get("token", "")).strip()
        if not token:
            return LicenseCheckResult(False, "Lisans dosyası bozuk.", None)

        try:
            payload = self._verify_token(token)
        except Exception as exc:
            return LicenseCheckResult(False, str(exc), None)

        try:
            expires_at = _parse_dt(str(payload["expires_at"]))
        except Exception:
            return LicenseCheckResult(False, "Bitiş tarihi okunamadı.", payload)

        if expires_at <= _utc_now():
            return LicenseCheckResult(False, "Lisans süresi dolmuş.", payload)

        stored_fp = str(record.get("machine_fingerprint", "")).strip()
        current_fp = get_machine_fingerprint()
        if stored_fp and stored_fp != current_fp:
            return LicenseCheckResult(False, "Bu lisans başka cihazda aktif.", payload)

        record["last_verified_at"] = _utc_now().isoformat()
        self._save_local_license(record)

        return LicenseCheckResult(True, "Lisans aktif.", payload)

    def deactivate(self) -> None:
        if self.license_path.exists():
            self.license_path.unlink()

    def days_left(self) -> Optional[int]:
        result = self.check_local_license()
        if not result.active or not result.payload:
            return None

        try:
            expires_at = _parse_dt(str(result.payload["expires_at"]))
        except Exception:
            return None

        delta = expires_at - _utc_now()
        return max(delta.days, 0)
