# backend/salesorderdetail/serializers.py
from rest_framework import serializers
from .models.models import SalesOrderMaster, SalesOrderDetail

class SalesOrderMasterSerializer(serializers.ModelSerializer):
    totals = serializers.SerializerMethodField()

    def get_totals(self, instance):
        return instance.calculate_totals()

    class Meta:
        model = SalesOrderMaster
        fields = [
            'master_unique_id', 'master_belge_giris_no', 'sip_no', 'satis_tipi', 'satici',
            'belge_tur', 'onay1_status', 'onay2_status', 'belge_tarihi', 'teslim_tarihi',
            'belge_onay', 'belge_status', 'belge_kur', 'belge_doviz', 'musteri_kod',
            'musteri_ad', 'totals'
        ]

class SalesOrderDetailSerializer(serializers.ModelSerializer):
    master_musteri_ad = serializers.SerializerMethodField()
    master_belge_tarihi = serializers.SerializerMethodField()
    master_sip_no = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderDetail
        fields = [
            'detay_unique_id', 'master', 'detay_belge_giris_no', 'kalem_grup', 'satir_status',
            'satir_no', 'depo_kod', 'kalem_kod', 'kalem_tanimi', 'birim', 'sip_miktar',
            'sevk_miktar', 'kalan_miktar', 'liste_fiyat_dpb', 'detay_kur', 'detay_doviz',
            'iskonto_oran', 'net_fiyat_dpb', 'brut_tutar_dpb', 'net_tutar_dpb', 'isk_tutar_dpb',
            'kdv_tutar_dpb', 'kdvli_net_tutar_dpb', 'liste_fiyat_ypb', 'brut_tutar_ypb',
            'isk_tutar_ypb', 'net_tutar_ypb', 'kdv_oran', 'kdv_tutar_ypb', 'kdvli_net_tutar_ypb',
            'master_belge_tarihi', 'master_sip_no', 'master_musteri_ad'
        ]

    def get_master_musteri_ad(self, obj):
        return obj.master.musteri_ad if obj.master else None

    def get_master_belge_tarihi(self, obj):
        return obj.master.belge_tarihi if obj.master else None

    def get_master_sip_no(self, obj):
        return obj.master.sip_no if obj.master else None
