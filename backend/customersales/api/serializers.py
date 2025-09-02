# backend/customersales/api/serializers.py

from rest_framework import serializers
from ..models import CustomerSalesRawData

# -----------------------------------------------------------------------------
# 1. READ-ONLY RAPOR SERİLEŞTİRİCİLERİ
# Bu serileştiriciler, PostgreSQL'deki ham veri tablolarından okunan verileri
# API için JSON formatına dönüştürür.
# -----------------------------------------------------------------------------

class CustomerSalesDataSerializer(serializers.ModelSerializer):
    """
    PostgreSQL'deki CustomerSalesRawData modelinden okunan verileri serileştirir.
    Bu, /data endpoint'inin çıktısını oluşturur. ModelSerializer kullandığımız
    için API dokümantasyonu (Swagger/Redoc) da otomatik olarak oluşacaktır.
    """
    class Meta:
        model = CustomerSalesRawData
        # Modeldeki tüm alanları API çıktısına dahil ediyoruz.
        fields = [
            'satici',
            'satis_tipi',
            'cari_grup',
            'musteri_kodu',
            'musteri_adi',
            'toplam_net_spb_eur',
            'ocak', 'subat', 'mart', 'nisan', 'mayis', 'haziran',
            'temmuz', 'agustos', 'eylul', 'ekim', 'kasim', 'aralik'
        ]


class CustomerSalesSummarySerializer(serializers.Serializer):
    """
    Servis katmanında .aggregate() ile hesaplanan genel özet (grand total)
    verisini serileştirir ve doğrular. Bu bir modelle doğrudan ilişkili
    olmadığı için standart Serializer kullanıyoruz.
    """
    # Servis dosyasındaki aggregate alan adlarıyla eşleşmeli
    ToplamNetSPB_EUR = serializers.DecimalField(max_digits=19, decimal_places=2)
    Ocak = serializers.DecimalField(max_digits=19, decimal_places=2)
    Şubat = serializers.DecimalField(max_digits=19, decimal_places=2)
    Mart = serializers.DecimalField(max_digits=19, decimal_places=2)
    Nisan = serializers.DecimalField(max_digits=19, decimal_places=2)
    Mayıs = serializers.DecimalField(max_digits=19, decimal_places=2)
    Haziran = serializers.DecimalField(max_digits=19, decimal_places=2)
    Temmuz = serializers.DecimalField(max_digits=19, decimal_places=2)
    Ağustos = serializers.DecimalField(max_digits=19, decimal_places=2)
    Eylül = serializers.DecimalField(max_digits=19, decimal_places=2)
    Ekim = serializers.DecimalField(max_digits=19, decimal_places=2)
    Kasım = serializers.DecimalField(max_digits=19, decimal_places=2)
    Aralık = serializers.DecimalField(max_digits=19, decimal_places=2)

