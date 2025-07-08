# backend/deliverydocsumv2/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from ..serializers import DeliveryDocSummarySerializer
from ..models.models import DeliveryDocSummary
from ..utilities.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from loguru import logger

class DeliveryDocSummaryListView(APIView):
    """
    Django lokal veritabanındaki tüm DeliveryDocSummary kayıtlarını listeler.
    """
    def get(self, request, *args, **kwargs):
        cached_data = cache.get('delivery_doc_summaries')
        if not cached_data:
            summaries = DeliveryDocSummary.objects.all()
            serializer = DeliveryDocSummarySerializer(summaries, many=True)
            cache.set('delivery_doc_summaries', serializer.data, timeout=30)  # 30 saniye cache süresi
            return Response(serializer.data)
        return Response(cached_data)
    

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
        if not token:
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = fetch_hana_db_data(token)
            if not data:  # Veri yoksa uygun bir cevap dön
                return Response({"error": "Veri alınamadı veya boş."}, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                # Mevcut tüm kayıtları sil
                DeliveryDocSummary.objects.all().delete()
                # Yeni verileri oluştur
                for item in data:
                    DeliveryDocSummary.objects.create(
                        cari_kod=item['CariKod'],
                        cari_adi=item.get('CariAdi', ''),
                        temsilci=item.get('Temsilci', ''),
                        cari_grup=item.get('CariGrup', ''),
                        bugun=item.get('Bugun', 0),
                        bugun_minus_1=item.get('BugunMinus1', 0),
                        bugun_minus_2=item.get('BugunMinus2', 0),
                        bugun_minus_3=item.get('BugunMinus3', 0),
                        bugun_minus_4=item.get('BugunMinus4', 0),
                        bu_ay_toplam=item.get('BuAyToplam', 0),
                        bu_ay_minus_1_toplam=item.get('BuAyMinus1Toplam', 0),
                        acik_sevkiyat_toplami=item.get('AcikSevkiyatToplami', 0),
                        yillik_toplam=item.get('YillikToplam', 0),
                        acik_siparis_toplami=item.get('AcikSiparisToplami', 0),
                        irsaliye_sayisi=item.get('IrsaliyeSayisi', 0),
                        bugun_ilgili_siparis_numaralari=item.get('BugunIlgiliSiparisNumaralari', '0'),
                        bugun_minus_1_ilgili_siparis_numaralari=item.get('BugunMinus1IlgiliSiparisNumaralari', '0'),
                        bugun_minus_2_ilgili_siparis_numaralari=item.get('BugunMinus2IlgiliSiparisNumaralari', '0'),
                        bugun_minus_3_ilgili_siparis_numaralari=item.get('BugunMinus3IlgiliSiparisNumaralari', '0'),
                        bugun_minus_4_ilgili_siparis_numaralari=item.get('BugunMinus4IlgiliSiparisNumaralari', '0'),
                        bu_ay_ilgili_siparis_numaralari=item.get('BuAyIlgiliSiparisNumaralari', '0'),
                        bu_ay_minus_1_ilgili_siparis_numaralari=item.get('BuAyMinus1IlgiliSiparisNumaralari', '0'),
                        acik_irsaliye_belge_no_tarih_tutar=item.get('AcikIrsaliyeBelgeNoTarihTutar', '0')
                    )
            cache.delete('delivery_doc_summaries')
            return Response(
                {
                    "success": True,          # 👈 eklendi
                    "message": "HANA DB verileri başarıyla güncellendi ve cache temizlendi."
                },
                status=status.HTTP_200_OK
            )


        except Exception as e:
            logger.error(f"HANA verileri çekerken hata oluştu: {e}")
            return Response({
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
