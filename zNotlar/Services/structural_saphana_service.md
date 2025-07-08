# SAP HANA Servis Yapılandırma Raporu

**Oluşturulma Tarihi:** 2025-06-09 15:53:36

## ⚙️ SAP HANA Bağlantı Yapılandırması
Bağlantı ayarları, `/var/www/sapb1reportsv2/backend/hanadbcon/utilities/hanadb_config.py` dosyasından alınmıştır.

### HANA Veritabanı Bağlantı Ayarları
    - **Host**: `10.131.212.112`
    - **Port**: `30015`
    - **Kullanıcı**: `READONLYUSER`
    - **Parola**: `******` (Gizli)

## 📦 SAP HANA Servis Yönetim Komutları
```bash
sudo systemctl status hanadbcon
sudo systemctl restart hanadbcon
sudo systemctl stop hanadbcon
sudo systemctl start hanadbcon
sudo journalctl -u hanadbcon -n 100
```
## 🔍 SAP HANA Configuration Dosyası: 
```python
from hdbcli import dbapi
from django.conf import settings

def create_connection():
    try:
        connection = dbapi.connect(
            address=settings.HANADB_HOST,
            port=int(settings.HANADB_PORT),
            user=settings.HANADB_USER,
            password=settings.HANADB_PASS,
            autocommit=True
        )
        return connection
    except dbapi.Error as e:
        logger.error(f'HANA veritabanına bağlanırken hata: {str(e)}')
        return None
```
## 🧪 Bağlantı Testi
```bash
python3 -c '
from hdbcli import dbapi
from django.conf import settings
try:
    connection = dbapi.connect(
        address="10.131.212.112",
        port="30015",
        user="READONLYUSER",
        password="Eropa2018**",
        autocommit=True
    )
    print("✅ HANA bağlantısı başarılı")
except Exception as e:
    print(f'❌ Bağlantı başarısız: {str(e)}')
'
```

## 🧠 Ek Notlar
- SAP HANA veritabanı bağlantı ayarları `hanadb_config.py` dosyasındaki yapılandırmaya dayanır.
- SAP HANA'ya bağlantı için `hdbcli` kullanılır. Bağlantı hataları için loglar kontrol edilebilir.
- SAP HANA servisi, sistemde `systemd` ile yönetilmektedir.

👉 *Otomatik oluşturulmuştur. Manuel değişiklikleri üzerine yazmayın.*
