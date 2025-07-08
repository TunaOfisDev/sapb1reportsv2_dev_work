user@reportserver:~$ isql -v LOGO readOnlyUser Logo142536*
+---------------------------------------+
| Connected!                            |
|                                       |
| sql-statement                         |
| help [tablename]                      |
| quit                                  |
|                                       |
+---------------------------------------+
SQL> SELECT 
    CLCARD.CODE AS CustomerCode,
    CLCARD.DEFINITION_ AS CustomerName

FROM 
    LG_002_CLCARD CLCARD
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CustomerCode     | CustomerName                                                                                                                                                                                             |
+------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ÿ               |                                                                                                                                                                                                          |
| 120.60.01.A001   | Aıda Tur Sey Acent Ltd.Şti.                                                                                                                                                                            |
| 120.60.01.A002   | Al Harran                                                                                                                                                                                                |
| 120.60.01.A003   | Alsahhap Turizm İnş.Gıda Teks.Rekl.San.İç VE Dış Tic.                                                                                                                                             |
| 120.60.01.A004   | American Consulate General Istanbul                                                                                                                                                                      |
| 120.60.01.B001   | Bella Vita Seyahat Hizmetleri Turizm Ltd. Sti.                                                                                                                                                           |
| 120.60.01.B002   | Bakü Prodüksüyon Kongre Org.Özel Eğitim Dan.Ve Tic.                                                                                                                                                 |
| 120.60.01.B003   | Btravel Turizm Aş. 

***************************************************

Görünüşe göre, `readOnlyUser` kullanıcısının `TIGERDB` veritabanında `db_datareader` rolü atanmış durumda ve bu, sadece okuma izni için yeterlidir. Ancak, hala bağlanamıyorsanız birkaç ek kontrol yapmanız gerekebilir.

### Adım 1: ODBC Bağlantı Ayarlarını Kontrol Etme
Öncelikle, `odbc.ini` dosyanızın doğru yapılandırıldığından emin olun. `/etc/odbc.ini` dosyasını açarak şu şekilde kontrol edebilirsiniz:

```ini
[LOGO]
Description=Microsoft ODBC Driver 17 for SQL Server
Driver=ODBC Driver 17 for SQL Server
Server=81.8.112.74,1433
Database=TIGERDB
UID=readOnlyUser
PWD=Logo142536*
```

### Adım 2: ODBC Bağlantısını Terminalden Test Etme
Aşağıdaki komutu kullanarak ODBC bağlantısını test edebilirsiniz:

```sh
isql -v LOGO readOnlyUser Logo142536*
```

Eğer bu hala başarısız olursa, ODBC sürücüsü ile ilgili bir sorun olabilir veya sunucu tarafında bazı ek güvenlik ayarları yapılması gerekebilir.

### Adım 3: SQL Server Configuration Manager'da Ayarları Kontrol Etme
- **TCP/IP Protokolü:** TCP/IP protokolünün etkinleştirildiğinden emin olun. 
- **Bağlantı Noktası (Port):** SQL Server Configuration Manager'da TCP/IP ayarlarında 1433 numaralı bağlantı noktasının açık olduğundan ve uzaktan bağlantılara izin verildiğinden emin olun.

### Adım 4: Kullanıcı Yetkilerini Genişletme
Eğer yukarıdaki adımlar sorunu çözmezse, `readOnlyUser` kullanıcısına ek yetkiler vererek tekrar deneyin:

```sql
USE TIGERDB;
GO
ALTER ROLE db_datareader ADD MEMBER readOnlyUser;
GO
ALTER ROLE db_owner ADD MEMBER readOnlyUser;
```

Bu komutlar `readOnlyUser` kullanıcısına tam yetki verir. Bağlantı sorunlarını giderdikten sonra bu yetkileri `db_datareader` seviyesine geri çekebilirsiniz.

### Adım 5: SQL Server Loglarını Kontrol Etme
SQL Server'ın hata günlüklerini kontrol ederek bağlantı hatalarının ayrıntılarını görebilirsiniz. SSMS'te SQL Server Agent altında hata günlüklerini kontrol edin.

### Adım 6: Firewall Ayarlarını Kontrol Etme
SQL Server'ın çalıştığı sunucuda firewall ayarlarını kontrol edin. 1433 numaralı portun açık olduğundan ve dış bağlantılara izin verildiğinden emin olun.

### Özet
1. `odbc.ini` dosyanızın doğru yapılandırıldığını doğrulayın.
2. `isql` komutu ile ODBC bağlantısını test edin.
3. SQL Server Configuration Manager'da TCP/IP ve port ayarlarını kontrol edin.
4. Kullanıcı yetkilerini genişletmeyi deneyin.
5. SQL Server loglarını kontrol edin.
6. Firewall ayarlarını kontrol edin.

Bu adımları izleyerek `readOnlyUser` kullanıcısı ile başarılı bir ODBC bağlantısı sağlayabilirsiniz.