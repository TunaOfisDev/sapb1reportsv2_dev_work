# TARS - acik_emirler_cek.py v1.0
# Bu script, Binance'teki tüm açık spot emirlerini JSON formatında listeler.

import json
from binance.client import Client
from binance.exceptions import BinanceAPIException

# --- GÜVENLİ ALAN: API Anahtarlarını Buraya Gir ---
# BU BİLGİLERİ KİMSEYLE PAYLAŞMA!
API_KEY = "IFPq9aipHCXA0AqlBTaLXuqFIAjEYDn7tv4HJx7jLHDHhsrKa1Zr0tJbgCWNsY0Q"
SECRET_KEY = "JsbwEgjEiP96Z4kvLs338389UXxFsWPHz5MZIEPYboy6OUhRlLyuJDJKZJu6tRtQ"
# ----------------------------------------------------

try:
    # Binance'e bağlan
    client = Client(API_KEY, SECRET_KEY)

    # Tüm açık emirleri çek
    open_orders = client.get_open_orders()

    # Sonucu JSON formatında ekrana yazdır
    if not open_orders:
        print(json.dumps([{"mesaj": "Aktif açık emir bulunmuyor."}], indent=4))
    else:
        print(json.dumps(open_orders, indent=4))

    print("\n# Bilgi: emirler.json olarak kaydetmek için komut: python acik_emirler_cek.py > emirler.json")

except BinanceAPIException as e:
    print(f"Binance API Hatası: {e.status_code} - {e.message}")
except Exception as e:
    print(f"Beklenmedik bir hata oluştu: {e}")