# backend/productgroupdeliverysum/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .serializers import DeliverySummarySerializer
from ..models.delivery_summary import DeliverySummary
from ..utils.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from loguru import logger

class DeliverySummaryViewSet(viewsets.ModelViewSet):
    """
    Teslimat özetleri için CRUD işlemleri ve özel aksiyonlar.
    """
    queryset = DeliverySummary.objects.all()
    serializer_class = DeliverySummarySerializer
    permission_classes = [IsAuthenticated]  # Yetkilendirme için

    # Özel aksiyonlar (local-data ve fetch-hana) için `@action` kullanıyoruz

    @action(detail=False, methods=['get'], url_path='local-data')
    def get_local_data(self, request):
        """
        Yerel veritabanındaki tüm teslimat özetlerini cache kullanarak döner.
        """
        cached_data = cache.get('product_group_delivery_summaries')
        if not cached_data:
            summaries = DeliverySummary.objects.all()
            serializer = DeliverySummarySerializer(summaries, many=True)
            cache.set('product_group_delivery_summaries', serializer.data, timeout=30)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(cached_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='fetch-hana')
    def fetch_hana_data(self, request):
        """
        HANA DB'den veri çeker ve yerel veritabanına kaydeder.
        """
        token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
        if not token:
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = fetch_hana_db_data(token)
            if not data:
                return Response({"error": "Veri alınamadı veya boş."}, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                # Mevcut tüm kayıtları sil
                DeliverySummary.objects.all().delete()

                # Yeni verileri oluştur
                for item in data:
                    yil = item.get('Yil')  # 'Yil' büyük harfle geliyor
                    yil_ay = item.get('YilAy')  # 'YilAy' de büyük harfle geliyor

                    if not yil or not yil_ay:
                        logger.error(f"Veri eksik: yil veya yil_ay alanı boş. Geçilen veri: {item}")
                        continue

                    # Yeni kayıt oluştur
                    DeliverySummary.objects.create(
                        yil=yil,
                        yil_ay=yil_ay,
                        teslimat_tutar=item.get('ToplamTeslimatTutar', 0),
                        teslimat_girsberger=item.get('ToplamTeslimatGirsberger', 0),
                        teslimat_mamul=item.get('ToplamTeslimatMamul', 0),
                        teslimat_ticari=item.get('ToplamTeslimatTicari', 0),
                        teslimat_nakliye=item.get('ToplamTeslimatNakliye', 0),
                        teslimat_montaj=item.get('ToplamTeslimatMontaj', 0)
                    )

            # Cache'i temizliyoruz
            cache.delete('product_group_delivery_summaries')
            return Response({"message": "Veriler başarıyla kaydedildi."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"HANA verileri çekerken hata oluştu: {e}")
            return Response({
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=False, methods=['get'], url_path='year-comparison/(?P<year>[0-9]{4})')
    def get_year_comparison(self, request, year):
        """
        Belirtilen yıl ve önceki yılın verilerini döndürür
        """
        try:
            year = int(year)
            current_year_data = DeliverySummary.objects.filter(yil=str(year))
            previous_year_data = DeliverySummary.objects.filter(yil=str(year-1))

            current_serializer = DeliverySummarySerializer(current_year_data, many=True)
            previous_serializer = DeliverySummarySerializer(previous_year_data, many=True)

            return Response({
                'currentYear': current_serializer.data,
                'previousYear': previous_serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Yıl karşılaştırma verisi alınırken hata: {e}")
            return Response({
                'error': 'Veriler alınırken bir hata oluştu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)