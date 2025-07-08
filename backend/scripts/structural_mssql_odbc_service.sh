#!/bin/bash

# MSSQL Sistem Analiz ve Dokümantasyon Scripti
# Author: SAPB1Reports Assistant - TARZ
# Date: $(date '+%Y-%m-%d %H:%M:%S')

OUTPUT_PATH="/var/www/sapb1reportsv2/zNotlar/Services/structural_mssql_odbc_service.md"
ENV_PATH="/var/www/sapb1reportsv2/backend/.env"
MSSQL_CONF_PATH="/var/www/sapb1reportsv2/backend/odbc.ini"

# Ortam değişkenlerinden MSSQL bilgilerini al
LOGO_DB_HOST=$(grep 'LOGO_DB_HOST=' "$ENV_PATH" | cut -d '=' -f2)
LOGO_DB_PORT=$(grep 'LOGO_DB_PORT=' "$ENV_PATH" | cut -d '=' -f2)
LOGO_DB_USER=$(grep 'LOGO_DB_USER=' "$ENV_PATH" | cut -d '=' -f2)
LOGO_DB_PASS=$(grep 'LOGO_DB_PASS=' "$ENV_PATH" | cut -d '=' -f2)
LOGO_DB_NAME=$(grep 'LOGO_DB_NAME=' "$ENV_PATH" | cut -d '=' -f2)

echo "🚀 MSSQL servis bilgileri analiz ediliyor..."

{
echo "# MSSQL (ODBC + mssql-tools) Servis Yapılandırma Raporu"
echo ""
echo "**Oluşturulma Tarihi:** $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "## ⚙️ ODBC Yapılandırması"
echo "Yapılandırma dosyası \`/etc/odbc.ini\` üzerinden alınmıştır."
echo ""
echo "### MSSQL ODBC Ayarları"
echo "    - **Host**: \`$LOGO_DB_HOST\`"
echo "    - **Port**: \`$LOGO_DB_PORT\`"
echo "    - **Kullanıcı**: \`$LOGO_DB_USER\`"
echo "    - **Veritabanı**: \`$LOGO_DB_NAME\`"
echo ""

echo "## 🔧 ODBC Yapılandırma Dosyasından Ayarlar"
echo '```ini'
sudo cat /etc/odbc.ini | grep -E '^(Driver|Server|Database|UID|PWD)' | sed 's/^/    /'
echo '```'
echo ""

echo "## 🔍 MSSQL Servis Durumu"
echo '```bash'
echo "systemctl status mssql-server"
echo "systemctl restart mssql-server"
echo "systemctl stop mssql-server"
echo "systemctl start mssql-server"
echo "journalctl -u mssql-server -n 100"
echo '```'

echo "## 📦 SQLCMD Servis Yönetim Komutları"
echo '```bash'
echo "sqlcmd -S $LOGO_DB_HOST,$LOGO_DB_PORT -U $LOGO_DB_USER -P '$LOGO_DB_PASS' -d $LOGO_DB_NAME"
echo "sqlcmd -S $LOGO_DB_HOST,$LOGO_DB_PORT -U $LOGO_DB_USER -P '$LOGO_DB_PASS' -d $LOGO_DB_NAME -Q 'SELECT 1;'"
echo '```'

echo "## 🧪 Bağlantı Testi"
echo '```bash'
sqlcmd -S "$LOGO_DB_HOST","$LOGO_DB_PORT" -U "$LOGO_DB_USER" -P "$LOGO_DB_PASS" -d "$LOGO_DB_NAME" -Q "SELECT 1;" && echo '✅ Bağlantı başarılı' || echo '❌ Bağlantı başarısız'
echo '```'

echo ""
echo "## 🧠 Ek Notlar"
echo "- ODBC ile MSSQL veritabanına bağlanmak için \`ODBC Driver 17 for SQL Server\` kullanılır."
echo "- \`sqlcmd\` aracı ile komut satırından sorgular çalıştırılabilir."
echo "- Loglar için: \`journalctl -u mssql-server\` komutunu kullanabilirsiniz."

echo ""
echo "👉 *Otomatik oluşturulmuştur. Manuel değişiklikleri üzerine yazmayın.*"
} | sudo tee "$OUTPUT_PATH" > /dev/null

echo "✅ Rapor oluşturuldu: $OUTPUT_PATH"
