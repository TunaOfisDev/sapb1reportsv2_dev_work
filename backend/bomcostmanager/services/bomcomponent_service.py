# backend/bomcostmanager/services/bomcomponent_service.py

import logging
from django.db import transaction
from ..connect.bomcomponent_data_fetcher import fetch_hana_db_data
from ..helpers.bomcomponent_helper import parse_hana_component_data, update_bom_component_cost
from ..models.bomcomponent_models import BOMComponent

logger = logging.getLogger(__name__)

def update_components_from_hana(token, item_code=None):
    """
    SAP HANA’dan BOM bileşen verisini çeker. Eğer istek üzerine gönderilen item_code parametresi varsa,
    bu filtreyi de uygular. Her bir bileşeni parse edip, BOMComponent modeli üzerinden update_or_create yapar.
    Ardından, override ve çarpanlar göz önünde bulundurularak maliyet güncellemesini gerçekleştirir.

    Args:
        token (str): SAP HANA bağlantısı için kimlik doğrulama token'ı.
        item_code (str, optional): Belirli bir ürüne ait BOM bileşenlerini filtrelemek için ürün kodu.

    Returns:
        list: Güncellenen BOMComponent instance'larının listesi.
    """
    raw_data = fetch_hana_db_data(token, item_code=item_code)
    if not raw_data:
        logger.error("HANA DB'den veri alınamadı. Token veya item_code kontrol edilmeli.")
        return None

    updated_components = []
    
    for item in raw_data:
        try:
            # HANA’dan gelen veriyi model için uygun formata çeviriyoruz.
            component_dict = parse_hana_component_data(item)
            # Veritabanı işlemlerini atomic blok içerisinde gerçekleştiriyoruz.
            with transaction.atomic():
                # Unique identifier olarak main_item ve component_item_code kullanılıyor.
                component, created = BOMComponent.objects.update_or_create(
                    main_item=component_dict.get("main_item"),
                    component_item_code=component_dict.get("component_item_code"),
                    defaults=component_dict
                )
                # Override ve çarpanlar uygulanarak güncel maliyet hesaplanıyor.
                component = update_bom_component_cost(component)
            
            updated_components.append(component)
            action = "oluşturuldu" if created else "güncellendi"
            logger.info(f"{component.component_item_code} için {action}.")
        except Exception as e:
            logger.error(f"BOM bileşeni işlenirken hata oluştu. Veri: {item}. Hata: {e}")
            continue

    logger.debug("update_components_from_hana: Toplam güncellenen bileşen sayısı: %d", len(updated_components))
    return updated_components
