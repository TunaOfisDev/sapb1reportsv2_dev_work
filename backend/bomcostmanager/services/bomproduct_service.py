# backend/bomcostmanager/services/bomproduct_service.py

import logging
from django.db import transaction
from ..connect.bomproduct_data_fetcher import fetch_hana_db_data
from ..helpers.bomproduct_helper import parse_hana_product_data, update_bom_product_record
from ..models.bomproduct_models import BOMProduct

logger = logging.getLogger(__name__)

def update_products_from_hana(token):
    """
    SAP HANA'dan BOM ürün verisini çekip, BOMProduct modelinde günceller.
    Token ile bağlantı sağlanır, ham veri parse edilip get_or_create ile kayıt eklenir;
    eğer kayıt zaten varsa update işlemi gerçekleştirilir. Her ürünün en son veri
    çekilme zamanı güncellenir.
    
    Returns:
        list: Güncellenen veya oluşturulan BOMProduct instance'larının listesi.
    """
    logger.debug("update_products_from_hana: İşlem başlatılıyor. Token: %s", token)
    raw_data = fetch_hana_db_data(token)
    if raw_data is None:
        logger.error("SAP HANA'dan ürün verisi alınamadı (raw_data None). Token veya bağlantı kontrol edilmeli.")
        return []
    
    if not raw_data:
        logger.info("SAP HANA'dan boş veri döndü.")
        return []
    
    logger.debug("SAP HANA'dan alınan ham veri: %s", raw_data)
    
    updated_products = []
    for item in raw_data:
        try:
            # SAP HANA'dan gelen veriyi, BOMProduct modeline uygun formata parse ediyoruz.
            product_data = parse_hana_product_data(item)
            logger.debug("Parsed product data: %s", product_data)
            with transaction.atomic():
                # Unique identifier olarak item_code kullanılarak kayıt ekleniyor veya güncelleniyor.
                product, created = BOMProduct.objects.get_or_create(
                    item_code=product_data.get("item_code"),
                    defaults=product_data
                )
                if not created:
                    product = update_bom_product_record(product, product_data)
            updated_products.append(product)
            action = "oluşturuldu" if created else "güncellendi"
            logger.info("Ürün %s: %s", action, product.item_code)
        except Exception as e:
            logger.exception("Ürün verisi işlenirken hata oluştu. Ürün verisi: %s. Hata: %s", item, e)
            continue

    logger.debug("update_products_from_hana: Toplam güncellenen/oluşturulan ürün sayısı: %d", len(updated_products))
    return updated_products
