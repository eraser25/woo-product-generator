"""
Yüklenen görseller için hash tabanlı URL hafızası.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional


class ImageCache:
    """Aynı görsel tekrar yüklenirse önceki public URL'i döndürür."""

    def __init__(self, cache_path: str | Path = "data/uploads/image_cache.json") -> None:
        self.cache_path = Path(cache_path)
        self._data = self._load()

    def _load(self) -> dict:
        if not self.cache_path.exists():
            return {}
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def digest(self, file_bytes: bytes) -> str:
        return hashlib.sha1(file_bytes).hexdigest()

    def get(self, file_bytes: bytes) -> Optional[str]:
        return self._data.get(self.digest(file_bytes))

    def set(self, file_bytes: bytes, url: str) -> None:
        self._data[self.digest(file_bytes)] = url
        self.save()

    def clear(self) -> None:
        self._data = {}
        if self.cache_path.exists():
            self.cache_path.unlink()
