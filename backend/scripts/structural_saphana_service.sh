#!/bin/bash

# SAP HANA Sistem Analiz ve Dokümantasyon Scripti
# Author: SAPB1Reports Assistant - TARZ
# Date: $(date '+%Y-%m-%d %H:%M:%S')

OUTPUT_PATH="/var/www/sapb1reportsv2/zNotlar/Services/structural_saphana_service.md"
ENV_PATH="/var/www/sapb1reportsv2/backend/.env"
HANADB_CONF_PATH="/var/www/sapb1reportsv2/backend/hanadbcon/utilities/hanadb_config.py"

# Ortam değişkenlerinden SAP HANA bilgilerini al
HANADB_HOST=$(grep 'HANADB_HOST=' "$ENV_PATH" | cut -d '=' -f2)
HANADB_PORT=$(grep 'HANADB_PORT=' "$ENV_PATH" | cut -d '=' -f2)
HANADB_USER=$(grep 'HANADB_USER=' "$ENV_PATH" | cut -d '=' -f2)
HANADB_PASS=$(grep 'HANADB_PASS=' "$ENV_PATH" | cut -d '=' -f2)

echo "🚀 SAP HANA servis bilgileri analiz ediliyor..."

{
echo "# SAP HANA Servis Yapılandırma Raporu"
echo ""
echo "**Oluşturulma Tarihi:** $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "## ⚙️ SAP HANA Bağlantı Yapılandırması"
echo "Bağlantı ayarları, \`$HANADB_CONF_PATH\` dosyasından alınmıştır."
echo ""
echo "### HANA Veritabanı Bağlantı Ayarları"
echo "    - **Host**: \`$HANADB_HOST\`"
echo "    - **Port**: \`$HANADB_PORT\`"
echo "    - **Kullanıcı**: \`$HANADB_USER\`"
echo "    - **Parola**: \`$HANADB_PASS\` (Gizli)"
echo ""

echo "## 📦 SAP HANA Servis Yönetim Komutları"
echo '```bash'
echo "sudo systemctl status hanadbcon"
echo "sudo systemctl restart hanadbcon"
echo "sudo systemctl stop hanadbcon"
echo "sudo systemctl start hanadbcon"
echo "sudo journalctl -u hanadbcon -n 100"
echo '```'

echo "## 🔍 SAP HANA Configuration Dosyası: `hanadb_config.py`"
echo '```python'
echo "from hdbcli import dbapi"
echo "from django.conf import settings"
echo ""
echo "def create_connection():"
echo "    try:"
echo "        connection = dbapi.connect("
echo "            address=settings.HANADB_HOST,"
echo "            port=int(settings.HANADB_PORT),"
echo "            user=settings.HANADB_USER,"
echo "            password=settings.HANADB_PASS,"
echo "            autocommit=True"
echo "        )"
echo "        return connection"
echo "    except dbapi.Error as e:"
echo "        logger.error(f'HANA veritabanına bağlanırken hata: {str(e)}')"
echo "        return None"
echo '```'

echo "## 🧪 Bağlantı Testi"
echo '```bash'
echo "python3 -c '"
echo "from hdbcli import dbapi"
echo "from django.conf import settings"
echo "try:"
echo "    connection = dbapi.connect("
echo "        address=\"$HANADB_HOST\","
echo "        port=\"$HANADB_PORT\","
echo "        user=\"$HANADB_USER\","
echo "        password=\"$HANADB_PASS\","
echo "        autocommit=True"
echo "    )"
echo "    print(\"✅ HANA bağlantısı başarılı\")"
echo "except Exception as e:"
echo "    print(f'❌ Bağlantı başarısız: {str(e)}')"
echo "'"
echo '```'

echo ""
echo "## 🧠 Ek Notlar"
echo "- SAP HANA veritabanı bağlantı ayarları \`hanadb_config.py\` dosyasındaki yapılandırmaya dayanır."
echo "- SAP HANA'ya bağlantı için \`hdbcli\` kullanılır. Bağlantı hataları için loglar kontrol edilebilir."
echo "- SAP HANA servisi, sistemde \`systemd\` ile yönetilmektedir."

echo ""
echo "👉 *Otomatik oluşturulmuştur. Manuel değişiklikleri üzerine yazmayın.*"
} | sudo tee "$OUTPUT_PATH" > /dev/null

echo "✅ Rapor oluşturuldu: $OUTPUT_PATH"
