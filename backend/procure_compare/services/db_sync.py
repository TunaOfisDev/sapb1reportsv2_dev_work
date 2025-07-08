# File: backend/procure_compare/services/db_sync.py

import logging
from procure_compare.models import PurchaseComparison
from procure_compare.services.transformer import transform_procure_compare_data

logger = logging.getLogger("procure_compare")  # 🔥 merkezi log kontrol

def sync_procure_compare_data(raw_data):
    """
    SAP HANA'dan gelen verileri dönüştürür ve veritabanına kaydeder.
    Mevcut verileri siler, yenilerini topluca ekler.
    """

    try:
        transformed_data = transform_procure_compare_data(raw_data)

        if not transformed_data:
            return

        # Sadece hata varsa log yazılır
        empty_quotes = [d for d in transformed_data if not d.get("teklif_fiyatlari_list")]
        if empty_quotes:
            logger.error(f"{len(empty_quotes)} kayıt 'teklif_fiyatlari_list' alanı boş!")

        # Eski veriyi temizle
        PurchaseComparison.objects.all().delete()

        # Yeni veriyi ekle
        comparisons = [PurchaseComparison(**item) for item in transformed_data]
        PurchaseComparison.objects.bulk_create(comparisons)

        # Başarı loglanmaz — sistem sessiz çalışır

    except Exception as e:
        logger.exception(f"Senkronizasyon sırasında hata oluştu: {e}")
