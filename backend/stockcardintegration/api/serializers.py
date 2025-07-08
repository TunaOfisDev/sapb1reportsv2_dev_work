# path: backend/stockcardintegration/api/serializers.py

from rest_framework import serializers
from ..models.models import StockCard, ITEMS_GROUP_DEFAULTS
from ..models.helptext import FieldHelpText  


class FieldHelpTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldHelpText
        fields = ["id", "field_name", "label", "description"]
        read_only_fields = fields


class BulkStockCardSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        instances = []
        for item in validated_data:
            item["extra_data"] = ITEMS_GROUP_DEFAULTS.get(item.get("items_group_code"), {})
            instances.append(StockCard(**item))
        return StockCard.objects.bulk_create(instances)


class StockCardSerializer(serializers.ModelSerializer):
    extra_data = serializers.SerializerMethodField(read_only=True)
    user_email = serializers.SerializerMethodField(read_only=True)  #  yeni alan
    U_eski_bilesen_kod = serializers.SerializerMethodField() 

    class Meta:
        model = StockCard
        list_serializer_class = BulkStockCardSerializer
        fields = (
            "id",
            "item_code",
            "item_name",
            "items_group_code",
            "price",
            "currency",
            "extra_data",
            "U_eski_bilesen_kod", 
            "hana_status",
            "last_synced_at",
            "created_at",
            "updated_at",
            "user_email",  #  yeni alanı ekledik
        )
        read_only_fields = (
            "id", "extra_data", "hana_status", "last_synced_at", "created_at", "updated_at", "user_email"
        )
        
    def get_U_eski_bilesen_kod(self, obj):
        if isinstance(obj.extra_data, dict):
            return obj.extra_data.get("U_eski_bilesen_kod")
        return None

    def get_user_email(self, obj):
        return obj.created_by.email if obj.created_by else None
    
    
    def get_extra_data(self, obj):
        return obj.extra_data if isinstance(obj.extra_data, dict) else {}


    def validate_item_code(self, value):
        if len(value) > 50:
            raise serializers.ValidationError("Stok Kodu en fazla 50 karakter olabilir!")
        if self.instance and self.instance.item_code == value:
            return value
        existing = StockCard.objects.filter(item_code=value).first()
        if existing and existing.hana_status == "completed":
            raise serializers.ValidationError("Bu item code alanına sahip stock card zaten SAP'ya gönderilmiş.")
        return value

    def validate_item_name(self, value):
        if len(value) > 200:
            raise serializers.ValidationError("Stok Tanımı en fazla 200 karakter olabilir!")
        return value

    def validate_items_group_code(self, value):
        if value not in ITEMS_GROUP_DEFAULTS:
            raise serializers.ValidationError("Geçersiz ürün grubu kodu! Sadece 105, 103 ve 112 geçerlidir.")
        return value

    def to_internal_value(self, data):
        mapped_data = {
            "item_code": data.get("item_code") or data.get("ItemCode"),
            "item_name": data.get("item_name") or data.get("ItemName"),
            "items_group_code": data.get("items_group_code") or data.get("ItemsGroupCode"),
            "price": data.get("price") or data.get("Price"),
            "currency": data.get("currency") or data.get("Currency"),
            "U_eski_bilesen_kod": data.get("U_eski_bilesen_kod"),
            "SalesVATGroup": data.get("SalesVATGroup")
        }
        return super().to_internal_value(mapped_data)



    def create(self, validated_data):
        extra = ITEMS_GROUP_DEFAULTS.get(validated_data.get("items_group_code"), {})
        u_eski_kod = self.initial_data.get("U_eski_bilesen_kod")
        if u_eski_kod:
            extra["U_eski_bilesen_kod"] = u_eski_kod
        validated_data["extra_data"] = extra
        return super().create(validated_data)


    def update(self, instance, validated_data):
        # Ürün grubu değişmişse defaultları güncelle
        if "items_group_code" in validated_data and validated_data["items_group_code"] != instance.items_group_code:
            validated_data["extra_data"] = ITEMS_GROUP_DEFAULTS.get(validated_data["items_group_code"], {})

        # Eski Bileşen Kodunu frontend'den alıyorsak güncelle
        u_eski_kod = self.initial_data.get("U_eski_bilesen_kod")
        if u_eski_kod is not None:
            # instance.extra_data'nın bozuk gelmesini önlemek için korumalı yapıyoruz
            if not isinstance(instance.extra_data, dict):
                instance.extra_data = {}
            instance.extra_data["U_eski_bilesen_kod"] = u_eski_kod
            instance.save(update_fields=["extra_data"])  # Sadece bu alanı güncelle

        return super().update(instance, validated_data)


    def delete(self, instance):
        raise serializers.ValidationError("Bu veri silinemez! HANA DB üzerinde DELETE işlemi yasaktır.")
