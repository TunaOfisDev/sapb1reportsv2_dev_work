# backend/rawmaterialwarehousestock/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models.models import RawMaterialWarehouseStock

class RawMaterialWarehouseStockSerializer(serializers.ModelSerializer):
    """
    Hammadde Depo Stok model serileştiricisi.
    """
    depo_kodu = serializers.CharField(required=False, allow_blank=True)
    kalem_grup_ad = serializers.CharField(required=False, allow_blank=True)
    stok_kalem = serializers.BooleanField(required=False)
    satis_kalem = serializers.BooleanField(required=False)
    satinalma_kalem = serializers.BooleanField(required=False)
    yapay_kalem = serializers.BooleanField(required=False)
    kalem_kod = serializers.CharField(validators=[UniqueValidator(queryset=RawMaterialWarehouseStock.objects.all())])
    kalem_tanim = serializers.CharField(required=False, allow_blank=True)
    stok_olcu_birim = serializers.CharField(required=False, allow_blank=True)
    depo_stok = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    siparis_edilen_miktar = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    son_satinalma_fiyat = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    son_satinalma_fatura_tarih = serializers.DateField(required=False, allow_null=True)
    verilen_siparisler = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = RawMaterialWarehouseStock
        fields = [
            'depo_kodu', 'kalem_grup_ad', 'stok_kalem', 'satis_kalem', 'satinalma_kalem',
            'yapay_kalem', 'kalem_kod', 'kalem_tanim', 'stok_olcu_birim', 'depo_stok',
            'siparis_edilen_miktar', 'son_satinalma_fiyat', 'son_satinalma_fatura_tarih',
            'verilen_siparisler', 'secili'
        ]

    def create(self, validated_data):
        """
        Yeni bir Hammadde Depo Stok kaydı oluşturur.
        """
        return RawMaterialWarehouseStock.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Mevcut bir Hammadde Depo Stok kaydını günceller.
        """
        instance.depo_kodu = validated_data.get('depo_kodu', instance.depo_kodu)
        instance.kalem_grup_ad = validated_data.get('kalem_grup_ad', instance.kalem_grup_ad)
        instance.stok_kalem = validated_data.get('stok_kalem', instance.stok_kalem)
        instance.satis_kalem = validated_data.get('satis_kalem', instance.satis_kalem)
        instance.satinalma_kalem = validated_data.get('satinalma_kalem', instance.satinalma_kalem)
        instance.yapay_kalem = validated_data.get('yapay_kalem', instance.yapay_kalem)
        instance.kalem_kod = validated_data.get('kalem_kod', instance.kalem_kod)
        instance.kalem_tanim = validated_data.get('kalem_tanim', instance.kalem_tanim)
        instance.stok_olcu_birim = validated_data.get('stok_olcu_birim', instance.stok_olcu_birim)
        instance.depo_stok = validated_data.get('depo_stok', instance.depo_stok)
        instance.siparis_edilen_miktar = validated_data.get('siparis_edilen_miktar', instance.siparis_edilen_miktar)
        instance.son_satinalma_fiyat = validated_data.get('son_satinalma_fiyat', instance.son_satinalma_fiyat)
        instance.son_satinalma_fatura_tarih = validated_data.get('son_satinalma_fatura_tarih', instance.son_satinalma_fatura_tarih)
        instance.verilen_siparisler = validated_data.get('verilen_siparisler', instance.verilen_siparisler)
        instance.verilen_siparisler = validated_data.get('secili', instance.verilen_siparisler)
        instance.save()
        return instance
