# productconfigv2/management/commands/setup_hana_queries.py
from django.core.management.base import BaseCommand
from hanadbcon.api.models import SQLQuery

class Command(BaseCommand):
    help = 'ProductConfigV2 için gerekli olan SAP HANA sorgularını oluşturur.'

    def handle(self, *args, **options):
        query_name = 'get_sap_price_by_itemcode'
        sql_text = """
            SELECT
                T1."Price"
            FROM {schema}."OITM" T0
            INNER JOIN {schema}."ITM1" T1 ON T0."ItemCode" = T1."ItemCode"
            WHERE T0."ItemCode" = ? AND T1."PriceList" = 1; -- PriceList ID'nizi doğrulayın (Örn: 1 = Ana Fiyat Listesi)
        """
        params = [{"name": "item_code", "type": "string", "description": "SAP Ürün Kodu"}]

        query, created = SQLQuery.objects.update_or_create(
            name=query_name,
            defaults={
                'query': sql_text,
                'parameters': params,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"'{query_name}' adlı HANA sorgusu başarıyla oluşturuldu."))
        else:
            self.stdout.write(self.style.SUCCESS(f"'{query_name}' adlı HANA sorgusu zaten vardı ve güncellendi."))