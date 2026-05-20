# WooCommerce CSV Kolonları

## Ana Kolonlar

| Kolon | Açıklama |
|---|---|
| ID | Ürün ID |
| Type | variable veya variation |
| SKU | Ürün SKU |
| Name | Ürün adı |
| Published | Yayın durumu |
| Regular price | Normal fiyat |
| Sale price | İndirimli fiyat |
| Categories | Kategori |
| Description | Açıklama |
| Short description | Kısa açıklama |
| Images | Görsel URL listesi |
| Parent | Parent SKU/ID |
| Position | Variation sırası |

---

## Attribute Kolonları

| Kolon | Açıklama |
|---|---|
| Attribute 1 name | Renk |
| Attribute 1 value(s) | Beyaz, Siyah |
| Attribute 1 visible | 1 |
| Attribute 1 global | 1 |

| Attribute 2 name | Beden |
| Attribute 2 value(s) | S, M, L, XL |
| Attribute 2 visible | 1 |
| Attribute 2 global | 1 |

---

## Images Alanı

Örnek:

https://site.com/a.jpg,https://site.com/b.jpg

Kurallar:
- İlk görsel kapak
- Sonrakiler galeri

---

## Variation Yapısı

Parent ürün:
- Type = variable

Variation ürün:
- Type = variation
- Parent alanı dolu olmalı

---

## Örnek SKU

Parent:
KYX-TS-0001

Variation:
KYX-TS-0001-BYZ-S
KYX-TS-0001-SYH-M

---

## Desteklenecek Renk Kodları

| Renk | Kod |
|---|---|
| Beyaz | BYZ |
| Siyah | SYH |
| Kırmızı | KRM |
| Mavi | MAV |
| Yeşil | YSL |

