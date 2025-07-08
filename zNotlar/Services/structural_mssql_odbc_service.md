# MSSQL (ODBC + mssql-tools) Servis Yapılandırma Raporu

**Oluşturulma Tarihi:** 2025-06-09 16:30:15

## ⚙️ ODBC Yapılandırması
Yapılandırma dosyası `/etc/odbc.ini` üzerinden alınmıştır.

### MSSQL ODBC Ayarları
    - **Host**: `81.8.112.74`
    - **Port**: `1433`
    - **Kullanıcı**: `sa`
    - **Veritabanı**: `TIGERDB`

## 🔧 ODBC Yapılandırma Dosyasından Ayarlar
```ini
```

## 🔍 MSSQL Servis Durumu
```bash
systemctl status mssql-server
systemctl restart mssql-server
systemctl stop mssql-server
systemctl start mssql-server
journalctl -u mssql-server -n 100
```
## 📦 SQLCMD Servis Yönetim Komutları
```bash
sqlcmd -S 81.8.112.74,1433 -U sa -P 'Q123456+' -d TIGERDB
sqlcmd -S 81.8.112.74,1433 -U sa -P 'Q123456+' -d TIGERDB -Q 'SELECT 1;'
```
## 🧪 Bağlantı Testi
```bash
           
-----------
          1

(1 rows affected)
✅ Bağlantı başarılı
```

## 🧠 Ek Notlar
- ODBC ile MSSQL veritabanına bağlanmak için `ODBC Driver 17 for SQL Server` kullanılır.
- `sqlcmd` aracı ile komut satırından sorgular çalıştırılabilir.
- Loglar için: `journalctl -u mssql-server` komutunu kullanabilirsiniz.

👉 *Otomatik oluşturulmuştur. Manuel değişiklikleri üzerine yazmayın.*
