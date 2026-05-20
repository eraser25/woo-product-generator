# Workflow

## Genel Akış

1. Kullanıcı ürün görsellerini toplu yükler.
2. Sistem dosya adlarını analiz eder.
3. Ürün adı ve renk ayrıştırılır.
4. Benzer ürün isimleri eşleştirilir.
5. Kullanıcı manuel düzenleme yapabilir.
6. Toplu fiyat/stok/kategori bilgileri girilir.
7. Sistem WooCommerce variable product yapısını oluşturur.
8. Variation ürünler otomatik üretilir.
9. WooCommerce uyumlu CSV export edilir.

---

## Dosya Adı Kuralları

Örnek:
- turtle_space_beyaz
- turtle_space_siyah

Kurallar:
- Son "_" sonrası renk kabul edilir.
- Öncesi ürün adı kabul edilir.
- Alt çizgiler boşluğa çevrilir.
- Baş harfler büyütülür.

Örnek:
turtle_space -> Turtle Space

---

## Variation Mantığı

Sabit bedenler:
- S
- M
- L
- XL

Her renk için tüm beden varyasyonları üretilir.

Örnek:
- Beyaz / S
- Beyaz / M
- Siyah / L

---

## Görsel Yönetimi

Kullanıcı virgülle ayrılmış URL listesi girer.

Örnek:
https://site.com/1.jpg,https://site.com/2.jpg

Kurallar:
- İlk URL ana görsel
- Sonraki URL’ler galeri görselleri

---

## SKU Yapısı

Parent:
KYX-TS-0001

Variation:
KYX-TS-0001-BYZ-S

Parçalar:
- KYX = marka kodu
- TS = tişört
- 0001 = ürün sıra numarası
- BYZ = renk kodu
- S = beden

---

## Manuel Eşleştirme

Sistem fuzzy matching kullanır.

Örnek:
- dead_pool
- deadpool
- dead pool

Benzer skorları kullanıcıya gösterilir.
Kullanıcı doğru ürünü seçebilir.

---

## CSV Export

Çıktı:
- WooCommerce import uyumlu CSV
- Variable + Variation yapısı
- Images alanı destekli
- SKU destekli
- Attribute destekli
