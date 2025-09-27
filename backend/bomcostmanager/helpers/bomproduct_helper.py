# backend/bomcostmanager/helpers/bomproduct_helper.py

import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from ..models.bomproduct_models import BOMProduct

logger = logging.getLogger(__name__)

def parse_hana_product_data(raw_data: dict) -> dict:
    """
    SAP HANA'dan çekilen BOM ürün verisini BOMProduct modeline uygun 
    bir sözlüğe çevirir. Hem Türkçe hem de İngilizce anahtar isimlerini 
    destekler. Tarih alanları için birden fazla formatı kontrol eder ve 
    en son veri çekilme zamanını UTC olarak günceller.

    Örnek raw_data:
    {
        "Ürün Kodu": "30.EMO.A16080.M1.E7",
        "Ürün Adı": "Örnek Ürün",
        "Varsayılan Depo": "Depo1",
        "Stok Kalemi": "Evet",
        "Satılabilir": "Evet",
        "Satın Alınabilir": "Hayır",
        "Satış Fiyat Listesi": "YOK",
        "Satış Fiyatı": "100.50",
        "Para Birimi": "TRY",
        "BOM Oluşturma Tarihi": "2023-03-15",
        "BOM Güncelleme Tarihi": "2023-04-01",
        "Oluşturan Kullanıcı Kodu": "USR01",
        "Güncelleyen Kullanıcı Kodu": "USR02"
    }

    Dönüş değeri, BOMProduct modelinde kullanılabilecek bir sözlüktür.
    """
    try:
        # Temel alanlar: hem Türkçe hem İngilizce anahtarları destekle
        item_code = raw_data.get("Ürün Kodu") or raw_data.get("ItemCode")
        item_name = raw_data.get("Ürün Adı") or raw_data.get("ItemName")
        default_wh = raw_data.get("Varsayılan Depo") or raw_data.get("DfltWH")
        
        # Boolean alanlar: "Evet"/"Hayır" veya doğrudan True/False
        invnt_item = (raw_data.get("Stok Kalemi") or raw_data.get("InvntItem", "N")) == "Evet"
        sell_item = (raw_data.get("Satılabilir") or raw_data.get("SellItem", "N")) == "Evet"
        purch_item = (raw_data.get("Satın Alınabilir") or raw_data.get("PrchseItem", "N")) == "Evet"

        sales_price_list = raw_data.get("Satış Fiyat Listesi") or raw_data.get("SalesPriceList", "YOK")
        try:
            sales_price = Decimal(raw_data.get("Satış Fiyatı") or raw_data.get("SalesPrice", "0"))
        except (InvalidOperation, TypeError):
            sales_price = Decimal("0")
            logger.warning("Geçersiz satış fiyatı değeri: %s", raw_data.get("Satış Fiyatı") or raw_data.get("SalesPrice"))
        currency = raw_data.get("Para Birimi") or raw_data.get("Currency", "TRY")
        
        # Tarih alanlarını farklı formatlarda kontrol et
        def parse_date(date_str):
            if not date_str:
                return None
            for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            logger.warning("Uygun tarih formatı bulunamadı: %s", date_str)
            return None

        bom_create_date = parse_date(raw_data.get("BOM Oluşturma Tarihi") or raw_data.get("BOMCreateDate"))
        bom_update_date = parse_date(raw_data.get("BOM Güncelleme Tarihi") or raw_data.get("BOMUpdateDate"))

        data = {
            "item_code": item_code,
            "item_name": item_name,
            "default_wh": default_wh,
            "invnt_item": invnt_item,
            "sell_item": sell_item,
            "purch_item": purch_item,
            "sales_price_list": sales_price_list,
            "sales_price": sales_price,
            "currency": currency,
            "bom_create_date": bom_create_date,
            "bom_update_date": bom_update_date,
            "created_user_code": raw_data.get("Oluşturan Kullanıcı Kodu") or raw_data.get("CreatedUser"),
            "updated_user_code": raw_data.get("Güncelleyen Kullanıcı Kodu") or raw_data.get("UpdatedUser"),
            "last_fetched_at": datetime.now(timezone.utc),
        }
        return data
    except (InvalidOperation, ValueError, TypeError) as e:
        logger.error("Error parsing HANA BOM product data: %s. Data: %s", e, raw_data)
        raise

def update_bom_product_record(bom_product: BOMProduct, new_data: dict) -> BOMProduct:
    """
    Verilen BOMProduct instance'ını, yeni gelen verilerle günceller.
    new_data, parse_hana_product_data() tarafından üretilen sözlük formatında olmalıdır.
    
    Bu fonksiyon, SAP HANA'dan gelen verilerle mevcut BOMProduct kaydını günceller
    ve en son veri çekilme zamanını (last_fetched_at) otomatik olarak set eder.
    """
    try:
        for field, value in new_data.items():
            setattr(bom_product, field, value)
        bom_product.save()
        return bom_product
    except Exception as e:
        logger.error("Error updating BOM product record for %s: %s", bom_product.item_code, e)
        raise
