# backend/salesbudgeteur/api/serializers.py

from rest_framework import serializers
from ..models.salesbudget_model import SalesBudgetEURModel, MonthlySalesBudgetEUR


class MonthlySalesBudgetEURSerializer(serializers.ModelSerializer):
    """
    Her bir ay için gerçek ve hedef EUR tutarlarını içerir.
    """
    class Meta:
        model = MonthlySalesBudgetEUR
        fields = ["ay", "gercek_tutar", "hedef_tutar"]


class SalesBudgetEURSerializer(serializers.ModelSerializer):
    """
    Satıcı bazında yıllık toplam satış, hedef, iptal, elle kapanan tutarları ve
    ilgili aylık detayları içeren üst seviye serializer.
    """
    aylik_veriler = MonthlySalesBudgetEURSerializer(many=True, read_only=True)

    class Meta:
        model = SalesBudgetEURModel
        fields = [
            "id",
            "satici",
            "yil",
            "toplam_gercek_eur",
            "toplam_hedef_eur",
            "toplam_iptal_eur",
            "toplam_elle_kapanan_eur",
            "kapali_sip_list",
            "aylik_veriler",
            "updated_at", 
        ]
