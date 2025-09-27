# File: procure_compare/tasks/sync_procure_data.py

from celery import shared_task
from procure_compare.models import PurchaseComparison
import logging

logger = logging.getLogger('procure_compare')


@shared_task(name="procure_compare.tasks.sync_procure_data.fetch_and_sync_procure_compare_data")
def fetch_and_sync_procure_compare_data():
    from procure_compare.services.hana_fetcher import fetch_hana_procure_compare_data
    raw_data = fetch_hana_procure_compare_data()
    sync_procure_compare_data(raw_data)


def sync_procure_compare_data(raw_data):
    """
    SAP'den gelen satınalma karşılaştırma verisini local DB'ye kaydeder.
    """
    PurchaseComparison.objects.all().delete()
    

    new_objects = []

    for item in raw_data:
        uniq_id = item.get('uniq_detail_no')
        item_code = item.get('kalem_kod')
        teklif_fiyatlari = item.get('teklif_fiyatlari_list', [])

        # Failsafe: teklif fiyatları boşsa logla ve işarete et
        if not teklif_fiyatlari:
            
            item['teklif_fiyatlari_list'] = [{
                'uyari': 'Bu kaleme ait teklif verisi eşleşemedi. SAP üzerinde kontrol önerilir.',
                'local_price': None
            }]

        try:
            new_obj = PurchaseComparison(
                uniq_detail_no=uniq_id,
                belge_no=item.get('belge_no'),
                kalem_kod=item_code,
                teklif_fiyatlari_list=item['teklif_fiyatlari_list'],
                # Diğer alanları da burada set et...
            )
            new_objects.append(new_obj)

        except Exception as e:
            logger.error(f"[ERR] Kayıt hatası: {uniq_id} → {e}")

    PurchaseComparison.objects.bulk_create(new_objects)
    
