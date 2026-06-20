"""
Ürün içe aktarma servisleri.
"""

from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List
import re

from src.core.color_parser import ColorParser
from src.utils.text_utils import ascii_key, normalize_text


class ImportService:
    """Yüklenen görselleri ürün gruplarına ayırır."""

    def __init__(self) -> None:
        self.color_parser = ColorParser()

    def _split_filename(self, filename: str):
        stem = Path(filename).stem.strip()

        # _ön, _arka, _1, _2 gibi galeri eklerini otomatik yakala
        match = re.search(r"_(ön|arka|front|back|\d+)$", stem, re.IGNORECASE)

        if match:
            position = match.group(1).lower()
            stem_without_position = stem[: match.start()]
        else:
            position = "ön"  # Ek yoksa varsayılan olarak ön yüz (ana görsel) kabul et
            stem_without_position = stem

        parts = [p for p in stem_without_position.split("_") if p]

        if len(parts) < 2:
            return None, None, position

        color_raw = parts[-1]
        base_raw = "_".join(parts[:-1])

        return base_raw, color_raw, position

    def process_uploaded_files(self, uploaded_files) -> List[Dict[str, Any]]:
        grouped = OrderedDict()

        if not uploaded_files:
            return []

        for file in uploaded_files:
            filename = file.name
            # Yeni fonksiyondan 3 değer (isim, renk, pozisyon) dönüyor
            base_raw, color_raw, position = self._split_filename(filename)

            if not base_raw or not color_raw:
                continue

            group_key = ascii_key(base_raw).replace("-", "_")

            if group_key not in grouped:
                grouped[group_key] = {
                    "group_key": group_key,
                    "original_name": base_raw,
                    "suggested_name": normalize_text(base_raw),
                    "colors": [],
                    "files": [],
                }

            color_info = self.color_parser.parse(color_raw)

            try:
                image_bytes = file.getvalue()
            except Exception:
                image_bytes = None

            color_entry = {
                "name": color_info["name"],
                "code": color_info["code"],
                "filename": filename,
                "image_bytes": image_bytes,
                "position": position,  # Ön/Arka sıralaması için eklendi
            }

            # Eskiden aynı renk varsa atlıyordu, şimdi galeri için içeri alıyoruz
            grouped[group_key]["colors"].append(color_entry)
            grouped[group_key]["files"].append(filename)

        # Ürünlerin ana görselleri (_ön) her zaman ilk sırada listelensin diye sıralıyoruz
        for key in grouped:
            grouped[key]["colors"].sort(
                key=lambda c: 0 if c.get("position") in ["ön", "front", "1"] else 1
            )

        return list(grouped.values())
