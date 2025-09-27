# backend/bomcostmanager/helpers/bomcomponent_helper.py

import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from ..models.bomcomponent_models import BOMComponent

logger = logging.getLogger(__name__)

def parse_hana_component_data(raw_data: dict) -> dict:
    """
    SAP HANA'dan çekilen BOM bileşen verisini BOMComponent modeline uygun
    bir sözlüğe çevirir. Ayrıca, kullanıcının override için gönderebileceği
    new_last_purchase_price, new_currency, labor_multiplier, overhead_multiplier,
    license_multiplier ve commission_multiplier gibi alanları opsiyonel olarak parse eder.

    Örnek raw_data (HANA + potansiyel override):
    {
        "MainItem": "30.EMO.A16080.M1.E7",
        "SubItem": "30.EMO.A16080.M1.E7",
        "ComponentItemCode": "151.AHS.M18.FLAP.V102",
        "ComponentItemName": "Örnek Bileşen Adı",
        "Quantity": "1",
        "Level": "0",
        "TypeDescription": "Kalem",
        "LastPurchasePrice": "58",
        "Currency": "TRY",
        "ExchangeRateUsed": "1",
        "LastPurchasePriceUPB": "58",
        "PriceSource": "YOK",
        "DocDate": "2023-03-15",
        "ComponentCostUPB": "58",
        "SalesPrice": "0",
        "SalesCurrency": "TRY",
        "PriceListName": "YOK",
        "ItemGroupName": "YARIMAMUL",

        // Opsiyonel override alanları:
        "NewLastPurchasePrice": "75",
        "NewCurrency": "USD",
        "LaborMultiplier": "1.05",
        "OverheadMultiplier": "1.10",
        "LicenseMultiplier": "1.00",
        "CommissionMultiplier": "1.00"
    }

    Dönüş değeri, BOMComponent modelinde kullanılabilecek bir sözlük şeklindedir.
    """
    try:
        # Tarih parse işlemi
        doc_date_str = raw_data.get("DocDate")
        if doc_date_str:
            try:
                doc_date = datetime.strptime(doc_date_str, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Tarih formatı beklenenden farklı: {doc_date_str}")
                doc_date = None
        else:
            doc_date = None

        # Bileşen stok kodu bulma
        component_item_code = raw_data.get("ComponentItemCode") or raw_data.get("ComponentItem")
        if not component_item_code:
            raise ValueError("component_item_code değeri boş olamaz (HANA datası yetersiz).")

        # Model için temel alanları parse etme
        data = {
            "main_item": raw_data.get("MainItem"),
            "sub_item": raw_data.get("SubItem") or raw_data.get("MainItem"),
            "component_item_code": component_item_code,
            "component_item_name": raw_data.get("ComponentItemName", ""),
            "quantity": Decimal(raw_data.get("Quantity", "0")),
            "level": int(raw_data.get("Level", 0)),
            "type_description": raw_data.get("TypeDescription", ""),
            "last_purchase_price": Decimal(raw_data.get("LastPurchasePrice", "0")),
            "currency": raw_data.get("Currency", "TRY"),
            "rate": Decimal(raw_data.get("ExchangeRateUsed", "1")),
            "last_purchase_price_upb": Decimal(raw_data.get("LastPurchasePriceUPB", "0")),
            "price_source": raw_data.get("PriceSource", "Taban Fiyat"),
            "doc_date": doc_date,
            "component_cost_upb": Decimal(raw_data.get("ComponentCostUPB", "0")),
            "sales_price": Decimal(raw_data.get("SalesPrice", "0")),
            "sales_currency": raw_data.get("SalesCurrency", "TRY"),
            "price_list_name": raw_data.get("PriceListName", "YOK"),
            "item_group_name": raw_data.get("ItemGroupName", "")
        }

        # Opsiyonel override alanlarını parse et
        new_last_purchase_str = raw_data.get("NewLastPurchasePrice", "0")
        new_currency_str = raw_data.get("NewCurrency", "")
        labor_multiplier_str = raw_data.get("LaborMultiplier", "1")
        overhead_multiplier_str = raw_data.get("OverheadMultiplier", "1")
        license_multiplier_str = raw_data.get("LicenseMultiplier", "1")
        commission_multiplier_str = raw_data.get("CommissionMultiplier", "1")

        # new_last_purchase_price
        try:
            new_last_purchase_price = Decimal(new_last_purchase_str)
        except (InvalidOperation, TypeError):
            new_last_purchase_price = Decimal("0")
            logger.warning(f"Geçersiz NewLastPurchasePrice: {new_last_purchase_str}, 0 olarak ayarlandı.")

        # labor_multiplier
        try:
            labor_multiplier = Decimal(labor_multiplier_str)
        except (InvalidOperation, TypeError):
            labor_multiplier = Decimal("1")
            logger.warning(f"Geçersiz LaborMultiplier: {labor_multiplier_str}, 1 olarak ayarlandı.")

        # overhead_multiplier
        try:
            overhead_multiplier = Decimal(overhead_multiplier_str)
        except (InvalidOperation, TypeError):
            overhead_multiplier = Decimal("1")
            logger.warning(f"Geçersiz OverheadMultiplier: {overhead_multiplier_str}, 1 olarak ayarlandı.")

        # license_multiplier
        try:
            license_multiplier = Decimal(license_multiplier_str)
        except (InvalidOperation, TypeError):
            license_multiplier = Decimal("1")
            logger.warning(f"Geçersiz LicenseMultiplier: {license_multiplier_str}, 1 olarak ayarlandı.")

        # commission_multiplier
        try:
            commission_multiplier = Decimal(commission_multiplier_str)
        except (InvalidOperation, TypeError):
            commission_multiplier = Decimal("1")
            logger.warning(f"Geçersiz CommissionMultiplier: {commission_multiplier_str}, 1 olarak ayarlandı.")

        data.update({
            "new_last_purchase_price": new_last_purchase_price,
            "new_currency": new_currency_str,
            "labor_multiplier": labor_multiplier,
            "overhead_multiplier": overhead_multiplier,
            "license_multiplier": license_multiplier,
            "commission_multiplier": commission_multiplier,
        })

        return data
    except (InvalidOperation, ValueError, TypeError) as e:
        logger.error(f"Error parsing HANA BOM component data: {e}. Data: {raw_data}")
        raise

def update_bom_component_cost(bom_component: BOMComponent) -> BOMComponent:
    """
    Verilen BOMComponent instance'ının güncel maliyetini (updated_cost)
    yeniden hesaplar ve kaydeder.

    Hesaplama mantığı:
      effective_price = (new_last_purchase_price > 0 ise override fiyat,
                         aksi halde last_purchase_price_upb)
      updated_cost = effective_price * labor_multiplier * overhead_multiplier
                     * license_multiplier * commission_multiplier

    Kaydetme sonrasında bom_component örneğini geri döndürür.
    """
    try:
        effective_price = (
            bom_component.new_last_purchase_price
            if bom_component.new_last_purchase_price and bom_component.new_last_purchase_price > 0
            else bom_component.last_purchase_price_upb
        )
        bom_component.updated_cost = (
            effective_price
            * bom_component.labor_multiplier
            * bom_component.overhead_multiplier
            * bom_component.license_multiplier
            * bom_component.commission_multiplier
        )
        bom_component.save()
        return bom_component
    except Exception as e:
        logger.error(f"Error updating BOM component cost for {bom_component.component_item_code}: {e}")
        raise
