"""
Görsel işlemleri yardımcıları
"""

from typing import List


def parse_image_urls(image_string: str) -> List[str]:
    """
    Virgülle ayrılmış URL listesini parse eder.

    İlk URL ana görsel olarak kullanılabilir.
    """
    if not image_string:
        return []

    return [
        url.strip()
        for url in image_string.split(",")
        if url.strip()
    ]


def get_main_image(image_urls: List[str]) -> str:
    """
    İlk görseli ana görsel olarak döndürür.
    """
    if not image_urls:
        return ""

    return image_urls[0]


def get_gallery_images(image_urls: List[str]) -> List[str]:
    """
    İlk görsel dışındaki galeriyi döndürür.
    """
    if len(image_urls) <= 1:
        return []

    return image_urls[1:]
