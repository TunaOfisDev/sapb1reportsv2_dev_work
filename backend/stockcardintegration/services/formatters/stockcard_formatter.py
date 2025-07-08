# backend/stockcardintegration/services/formatters/stockcard_formatter.py

from stockcardintegration.models.models import ITEMS_GROUP_DEFAULTS

def build_sap_stock_card_payload(stock_card):
    """
    Verilen StockCard instance'ını SAP HANA uyumlu JSON yapısına çevirir.
    """
    group_defaults = ITEMS_GROUP_DEFAULTS.get(stock_card.items_group_code, {})

    payload = {
        "ItemCode": stock_card.item_code,
        "ItemName": stock_card.item_name,
        "ItemType": group_defaults.get("ItemType", "itItems"),
        "ItemsGroupCode": stock_card.items_group_code,
        "SalesVATGroup": group_defaults.get("SalesVATGroup", "HES0010"),
        "PurchaseVATGroup": group_defaults.get("PurchaseVATGroup", "İND010"),
        "PurchaseItem": group_defaults.get("PurchaseItem", "tYES"),
        "SalesItem": group_defaults.get("SalesItem", "tYES"),
        "InventoryItem": group_defaults.get("InventoryItem", "tYES"),
        "ManageSerialNumbersOnReleaseOnly": group_defaults.get("ManageSerialNumbersOnReleaseOnly", "tNO"),
        "SalesUnit": group_defaults.get("SalesUnit", "Ad"),
        "PurchaseUnit": group_defaults.get("PurchaseUnit", "Ad"),
        "DefaultWarehouse": group_defaults.get("DefaultWarehouse", "M-01"),
        "InventoryUOM": group_defaults.get("InventoryUOM", "Ad"),
        "PlanningSystem": group_defaults.get("PlanningSystem", "M"),
        "ProcurementMethod": group_defaults.get("ProcurementMethod", "B"),
        "UoMGroupEntry": group_defaults.get("UoMGroupEntry", 1),
        "InventoryUoMEntry": group_defaults.get("InventoryUoMEntry", 1),
        "DefaultSalesUoMEntry": group_defaults.get("DefaultSalesUoMEntry", 1),
        "DefaultPurchasingUoMEntry": group_defaults.get("DefaultPurchasingUoMEntry", 1),
        "U_eski_bilesen_kod": stock_card.extra_data.get("U_eski_bilesen_kod", ""),
        "ItemPrices": [
            {
                "PriceList": 1,
                "BasePriceList": 1,
                "Factor": 1,
                "Price": float(stock_card.price),
                "Currency": stock_card.currency or "EUR"
            }
        ]
    }

    return payload
