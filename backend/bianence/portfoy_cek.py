# TARS - portfoy_cek.py v1.0
# Bu script, Binance spot cüzdanındaki güncel varlıkları JSON formatında listeler.

import json
from binance.client import Client
from binance.exceptions import BinanceAPIException

# --- GÜVENLİ ALAN: API Anahtarlarını Buraya Gir ---
# BU BİLGİLERİ KİMSEYLE PAYLAŞMA!
API_KEY='IFPq9aipHCXA0AqlBTaLXuqFIAjEYDn7tv4HJx7jLHDHhsrKa1Zr0tJbgCWNsY0Q'
SECRET_KEY='JsbwEgjEiP96Z4kvLs338389UXxFsWPHz5MZIEPYboy6OUhRlLyuJDJKZJu6tRtQ'
# ----------------------------------------------------

try:
    # Binance'e bağlan
    client = Client(API_KEY, SECRET_KEY)

    # Hesap bilgilerini çek
    account_info = client.get_account()

    # Sadece bakiyesi sıfırdan büyük olan varlıkları filtrele
    balances = account_info.get('balances', [])
    portfolio = [
        {
            "asset": item['asset'],
            "free": item['free'],
            "locked": item['locked']
        }
        for item in balances if float(item['free']) > 0 or float(item['locked']) > 0
    ]

    # Sonucu JSON formatında ekrana yazdır
    print(json.dumps(portfolio, indent=4))

    print("\n# Bilgi: portfoy.json olarak kaydetmek için komut: python portfoy_cek.py > portfoy.json")

except BinanceAPIException as e:
    print(f"Binance API Hatası: {e.status_code} - {e.message}")
except Exception as e:
    print(f"Beklenmedik bir hata oluştu: {e}")