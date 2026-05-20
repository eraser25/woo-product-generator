"""
WooCommerce REST API veri çekme servisi.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


@dataclass
class WooCommerceSiteData:
    categories: List[Dict[str, Any]]
    attributes: List[Dict[str, Any]]
    brands: List[Dict[str, Any]]


class WooCommerceAPIClient:
    """WooCommerce REST API üzerinden ürün yönetimi meta verilerini çeker."""

    def __init__(
        self,
        site_url: str,
        consumer_key: str,
        consumer_secret: str,
        timeout: int = 20,
    ) -> None:
        self.site_url = site_url.rstrip("/") + "/"
        self.consumer_key = consumer_key.strip()
        self.consumer_secret = consumer_secret.strip()
        self.timeout = timeout

    def _endpoint(self, path: str) -> str:
        return urljoin(self.site_url, f"wp-json/wc/v3/{path.lstrip('/')}")

    def _get(self, path: str, params: dict | None = None) -> Any:
        query = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
            "per_page": 100,
        }
        if params:
            query.update(params)

        url = f"{self._endpoint(path)}?{urlencode(query)}"
        request = Request(url, headers={"Accept": "application/json"})

        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"WooCommerce API HTTP {exc.code}: {detail}") from exc

    def test_connection(self) -> Dict[str, Any]:
        return self._get("system_status")

    def fetch_categories(self) -> List[Dict[str, Any]]:
        rows = self._get("products/categories", {"hide_empty": False})
        return [
            {"id": item.get("id"), "name": item.get("name", ""), "slug": item.get("slug", "")}
            for item in rows
        ]

    def fetch_attributes_with_terms(self) -> List[Dict[str, Any]]:
        attributes = self._get("products/attributes")
        result = []

        for attr in attributes:
            attr_id = attr.get("id")
            terms = []
            if attr_id:
                try:
                    terms = self._get(f"products/attributes/{attr_id}/terms", {"hide_empty": False})
                except Exception:
                    terms = []

            result.append({
                "id": attr_id,
                "name": attr.get("name", ""),
                "slug": attr.get("slug", ""),
                "terms": [
                    {"id": term.get("id"), "name": term.get("name", ""), "slug": term.get("slug", "")}
                    for term in terms
                ],
            })

        return result

    def fetch_brands(self, attributes: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
        try:
            rows = self._get("products/brands", {"hide_empty": False})
            return [
                {"id": item.get("id"), "name": item.get("name", ""), "slug": item.get("slug", "")}
                for item in rows
            ]
        except Exception:
            pass

        for attr in attributes or []:
            name = str(attr.get("name", "")).lower()
            slug = str(attr.get("slug", "")).lower()
            if "marka" in name or "brand" in name or slug in {"pa_marka", "pa_brand"}:
                return attr.get("terms", [])

        return []

    def fetch_site_data(self) -> WooCommerceSiteData:
        categories = self.fetch_categories()
        attributes = self.fetch_attributes_with_terms()
        brands = self.fetch_brands(attributes)
        return WooCommerceSiteData(categories=categories, attributes=attributes, brands=brands)
