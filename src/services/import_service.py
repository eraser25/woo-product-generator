"""
Ürün içe aktarma servisleri.
"""

from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List

from src.core.color_parser import ColorParser
from src.utils.text_utils import ascii_key, normalize_text


class ImportService:
    """Yüklenen görselleri ürün gruplarına ayırır."""

    def __init__(self) -> None:
        self.color_parser = ColorParser()

    def _split_filename(self, filename: str):
        stem = Path(filename).stem.strip()
        parts = [p for p in stem.split("_") if p]

        if len(parts) < 2:
            return None, None

        color_raw = parts[-1]
        base_raw = "_".join(parts[:-1])

        return base_raw, color_raw

    def process_uploaded_files(self, uploaded_files) -> List[Dict[str, Any]]:
        grouped = OrderedDict()

        if not uploaded_files:
            return []

        for file in uploaded_files:
            filename = file.name
            base_raw, color_raw = self._split_filename(filename)

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
            }

            if not any(c["code"] == color_entry["code"] for c in grouped[group_key]["colors"]):
                grouped[group_key]["colors"].append(color_entry)

            grouped[group_key]["files"].append(filename)

        return list(grouped.values())
