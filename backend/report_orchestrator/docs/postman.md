http://192.168.2.201/api/v2/report_orchestrator/reports/run/

Authorization  Bearer Token  `token`
body->raw json
POST Metot
{
  "api_name": "sofitel_supplier_balance_report"

}
yanit olumlu ise
{
    "message": "sofitel_balance_report için Celery görevi başlatıldı."
}

15saniye icinde rapor gelir gelmez ise backend/logs celery leri kontrol et

