# backend/girsbergerordropqt/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from ..serializers import OrdrDetailOpqtSerializer
from ..models.models import OrdrDetailOpqt
from ..utilities.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from loguru import logger

class OrdrDetailOpqtListView(APIView):
    """
    Django lokal veritabanındaki tüm OrdrDetailOpqt kayıtlarını listeler.
    """
    def get(self, request, *args, **kwargs):
        cached_data = cache.get('ordr_detail_opqt')
        if not cached_data:
            summaries = OrdrDetailOpqt.objects.all()
            serializer = OrdrDetailOpqtSerializer(summaries, many=True)
            cache.set('ordr_detail_opqt', serializer.data, timeout=30)  # 30 saniye cache süresi
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
                OrdrDetailOpqt.objects.all().delete()
                # Yeni verileri oluştur
                for item in data:
                    OrdrDetailOpqt.objects.create(
                        uniq_detail_no=item['UniqDetailNo'],
                        belge_no=item['BelgeNo'],
                        satici=item['Satici'],
                        belge_tarih=item['BelgeTarih'],
                        teslim_tarih=item['TeslimTarih'],
                        musteri_kod=item['MusteriKod'],
                        musteri_ad=item['MusteriAd'],
                        satis_tipi=item['SatisTipi'],
                        satir_status=item['SatirStatus'],
                        kalem_kod=item['KalemKod'],
                        kalem_tanimi=item['KalemTanimi'],
                        sip_miktar=item['SipMiktar'],
                        salma_teklif_tedarikci_kod=item.get('SalmaTeklifTedarikciKod', 'Yok'),
                        salma_teklif_tedarikci_ad=item.get('SalmaTeklifTedarikciAd', 'Yok'),
                        salma_teklif_no=item.get('SalmaTeklifNo', '0'),
                        salma_teklif_kaynak_detay_no=item.get('SalmaTeklifKaynakDetayNo', '0'),
                        salma_teklif_kalem_no=item.get('SalmaTeklifKalemNo', 'Yok'),
                        salma_teklif_miktar=item['SalmaTeklifMiktar'],
                    )
            cache.delete('ordr_detail_opqt')
            return Response({"message": "HANA DB verileri başarıyla güncellendi ve cache temizlendi."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"HANA verileri çekerken hata oluştu: {e}")
            return Response({
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
