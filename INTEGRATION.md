# Sunucusuz Lisans Sistemi Entegrasyonu

## 1) Bu klasörü projene ekle
`app_license/` klasörünü proje köküne koy.

## 2) `requirements.txt` içine şunu ekle
```text
cryptography
```

## 3) `app.py` içine lisans kapısı ekle
`streamlit` importlarından sonra:

```python
from app_license.license_screen import render_license_gate

if not render_license_gate(
    public_key_path="data/license/public_key.pem",
    license_path="data/license/license.json",
    support_email="seninmailin@siteadi.com",
    whatsapp_url="https://wa.me/90XXXXXXXXXX",
    website_url="https://siteadi.com",
):
    st.stop()
```

## 4) Public key dosyası
`data/license/public_key.pem` uygulamanın doğrulama anahtarıdır.

## 5) Lisans üretmek için
Önce key pair oluştur:

```bash
python -m app_license.license_generator init-keys --public data/license/public_key.pem --private tools/private_key.pem
```

Sonra lisans oluştur:

```bash
python -m app_license.license_generator issue --private tools/private_key.pem --customer "Ahmet" --plan monthly --days 30 --output licenses/ahmet_30d.key
```

## 6) Not
Bu sürüm sunucusuzdur.
Lisans, ilk aktive edilen bilgisayara bağlı olarak yerelde saklanır.
Tam sunuculu sistem kadar güçlü değildir ama hızlı başlangıç için uygundur.
