# backend/deliverydocsum/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from ..serializers import DeliveryDocSummarySerializer
from ..models.models import DeliveryDocSummary
from ..utilities.data_fetcher import fetch_hana_db_data
from loguru import logger

class DeliveryDocSummaryListView(APIView):
    """
    Django lokal veritabanındaki tüm DeliveryDocSummary kayıtlarını listeler.
    """
    def get(self, request, *args, **kwargs):
        summaries = DeliveryDocSummary.objects.all()
        serializer = DeliveryDocSummarySerializer(summaries, many=True)
        return Response(serializer.data)

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or ' ' not in token:
            return Response({"error": "Token sağlanmadı veya hatalı format."}, status=status.HTTP_401_UNAUTHORIZED)

        token = token.split(' ')[1]  # Bearer token formatında olduğundan dolayı

        try:
            data = fetch_hana_db_data(token)
            if data:
                with transaction.atomic():
                    # Mevcut tüm kayıtları sil
                    DeliveryDocSummary.objects.all().delete()
                    # Yeni verileri oluştur
                    for item in data:
                        DeliveryDocSummary.objects.create(
                            cari_kod=item['CariKod'],
                            cari_adi=item.get('CariAdi'),
                            temsilci=item.get('Temsilci'),
                            cari_grup=item.get('CariGrup'),
                            gunluk_toplam=item['GunlukToplam'],
                            dun_toplam=item['DunToplam'],
                            onceki_gun_toplam=item['OncekiGunToplam'],
                            aylik_toplam=item['AylikToplam'],
                            yillik_toplam=item['YillikToplam'],
                            acik_sevkiyat_toplami=item['AcikSevkiyatToplami'],
                            acik_siparis_toplami=item['AcikSiparisToplami'],
                            irsaliye_sayisi=item['IrsaliyeSayisi'],
                            gunluk_ilgili_siparis_numaralari=item.get('GunlukIlgiliSiparisNumaralari', '0'),
                            dun_ilgili_siparis_numaralari=item.get('DunIlgiliSiparisNumaralari', '0'),
                            onceki_gun_ilgili_siparis_numaralari=item.get('OncekiGunIlgiliSiparisNumaralari', '0')
                        )
                return Response({"message": "HANA DB verileri başarıyla güncellendi."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"HANA verileri çekerken hata oluştu: {e}")
            return Response({
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

