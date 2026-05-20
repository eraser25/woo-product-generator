# Lisans Aracı

Bu klasör geliştirici araçları içindir. Private key burada tutulabilir ama kaynak kontrolüne veya müşteri paketine eklenmemelidir.

## Key Üretmek

```bat
python -m app_license.license_generator init-keys --public data/license/public_key.pem --private tools/private_key.pem
```

## Lisans Üretmek

```bat
python -m app_license.license_generator issue --private tools/private_key.pem --customer "Ali" --plan monthly --days 30 --output licenses/ali_30d.key
```

`tools/private_key.pem` ve `licenses/*.key` `.gitignore` içindedir. Bu dosyaları müşterilere dağıtmayın.
