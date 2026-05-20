# Woo Product Generator

Streamlit tabanlı WooCommerce CSV üreticisidir. Ürün görsellerini dosya adından ürün ve renk gruplarına ayırır, variable parent + variation satırları üretir ve isteğe bağlı olarak görselleri FTP/FTPS ile sunucuya yükler.

## Kurulum

Python 3.11 veya üzeri kurulu olmalı ve `python` komutu PATH içinde görünmelidir.

```bat
baslat.bat
```

Betik `.venv` klasörünü oluşturur, bağımlılıkları kurar ve uygulamayı başlatır.

Elle çalıştırmak için:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Genel Ürün Kullanımı

Uygulama yalnızca tişört için çalışmak zorunda değildir. Sol menüdeki `Ürün adı son eki` alanına ürün tipini yazabilirsin:

```text
Baskılı Tişört
Seramik Kupa
Telefon Kılıfı
Poster
```

Bu alan boş bırakılırsa ürün adının sonuna otomatik metin eklenmez. `Ürün Tipi Kodu` alanını da ürününe göre değiştirebilirsin; örneğin kupa için `MUG`, telefon kılıfı için `CASE`.

## Görsel Dosya Formatı

Dosya adı şu yapıda olmalıdır:

```text
urun_adi_renk.jpg
```

Örnekler:

```text
space_cat_beyaz.jpg
space_cat_siyah.jpg
best_mom_kirmizi.png
```

Renkler Türkçe karakterli veya ASCII yazılabilir: `kırmızı` ve `kirmizi` aynı kabul edilir.

## Lisans

Uygulama imzalı offline lisans token'ı kullanır. Public key uygulamayla dağıtılır; private key yalnızca geliştiricide kalmalıdır.

Yerel lisans dosyası uygulama klasörüne değil kullanıcı profiline yazılır:

```text
%LOCALAPPDATA%\Woo Product Generator\license\license.json
```

`tools/private_key.pem`, `licenses/*.key` ve `data/license/license.json` kaynak depoya veya müşteri paketine eklenmemelidir.

## WooCommerce CSV

CSV çıktısı `data/uploads/csv/woocommerce_products.csv` altında oluşur ve arayüzden indirilebilir.

Üretilen yapı:

- Parent satırı: `variable`
- Variation satırları: `variation`
- Parent SKU: `MARKA-TIP-0001`
- Variation SKU: `MARKA-TIP-0001-RENK-BEDEN`
- Attribute 1: `Renk`
- Attribute 2: `Beden`

Tişört dışı ürünlerde `Bedenler` alanını varyasyon seçeneği gibi kullanabilirsin. Tek varyasyonlu ürünler için `Standart` seçeneğini seçmek yeterlidir.

## FTP Bağlantı Testi

Sol menüde FTP bilgilerini doldurduktan sonra `FTP Bağlantısını Test Et` butonuna basabilirsin. Test, sunucuya bağlanmayı ve hedef klasöre erişmeyi dener. Başarılıysa görsel yükleme öncesi bağlantının çalıştığını görürsün.

Test sırasında küçük bir geçici dosya yüklenir ve silinir. Böylece yalnızca bağlantı değil, hedef klasöre yazma izni ve public URL yapısı da kontrol edilir.

Yüklenen görseller `data/uploads/image_cache.json` içinde hash ile hatırlanır. Aynı görsel tekrar yüklenirse FTP'ye yeniden gönderilmez, önceki public URL kullanılır.

## WooCommerce REST API

Sol menüde aşağıdaki bilgileri girip `Site Bilgilerini Çek` butonuna basabilirsin:

```text
Site URL
Consumer Key
Consumer Secret
```

Uygulama API üzerinden şunları çeker:

- kategoriler
- attribute'lar
- attribute değerleri
- markalar

Markalar için önce WooCommerce Brands endpoint'i denenir. Sitede marka eklentisi yoksa `Marka` / `Brand` attribute'undan gelen değerler marka listesi olarak kullanılır.

## Dinamik Varyasyonlar

WooCommerce ayarları bölümünde istediğin attribute'ları seçebilirsin:

- Renk
- Beden
- Ayak Numarası
- Yaka Tipi
- WooCommerce sitesinden gelen diğer attribute'lar

Her attribute için WooCommerce'den gelen değerleri seçebilir veya manuel virgüllü değer yazabilirsin. CSV exporter seçilen attribute sayısına göre `Attribute 1`, `Attribute 2`, `Attribute 3` kolonlarını otomatik üretir.

## Yeni Ürün / Güncelleme

Sol menüde iki mod vardır:

- `Yeni ürün olarak oluştur`: yeni ID/SKU üretir ve sayaç ilerler.
- `Mevcut ürünü güncelle`: ürün grubu içinde girilen mevcut Woo ID ve SKU korunur. Variation satırları parent SKU'ya bağlı üretilir.

`Sayacı ve Hafızayı Sıfırla` butonu hem ürün ID sayacını hem de görsel hash hafızasını temizler.

## Test

```bat
.venv\Scripts\activate.bat
python -m pytest -q
```

## Müşteri Paketi

`woo-product-generator-Müşteri` klasörü dağıtım hazırlığı içindir. Installer artık `venv`, `build` ve eski çalışma çıktıları yerine yalnızca uygulama kaynaklarını ve gereksinim dosyalarını taşır. İlk açılışta `.venv` oluşturulur ve bağımlılıklar kurulur.
