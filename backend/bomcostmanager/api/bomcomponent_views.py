# backend/bomcostmanager/api/bomcomponent_views.py

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone

from ..models.bomcomponent_models import BOMComponent
from ..api.serializers import BOMComponentSerializer
from ..services.bomcomponent_service import update_components_from_hana
# from bomcostmanager.permissions import HasBOMProductAccess  # İzin sınıfı

logger = logging.getLogger(__name__)

class BOMComponentListView(APIView):
    """
    Yerel veritabanında saklanan tüm BOMComponent kayıtlarını listeler.
    Cache kullanılarak performanslı veri okunması sağlanır.
    """
    # permission_classes = [IsAuthenticated, HasBOMProductAccess]

    @method_decorator(cache_page(30))
    def get(self, request, *args, **kwargs):
        # Cache'de mevcut veriyi kontrol et
        cached_data = cache.get('bom_components')
        if cached_data:
            logger.debug("Cache'den BOMComponent verisi getirildi, kayıt sayısı: %d", len(cached_data))
            return Response(cached_data, status=status.HTTP_200_OK)

        components = BOMComponent.objects.all()
        serializer = BOMComponentSerializer(components, many=True)
        # Cache'e kaydet
        cache.set('bom_components', serializer.data, timeout=30)
        logger.debug("BOMComponent listesi sorgulandı ve cache'e kaydedildi, kayıt sayısı: %d", len(serializer.data))
        return Response(serializer.data, status=status.HTTP_200_OK)


class BOMComponentFetchView(APIView):
    """
    SAP HANA’dan canlı BOMComponent verilerini çeker ve yerel veritabanını günceller.
    İsteğe bağlı olarak, query parametresi ile gönderilen item_code değeri SAP HANA sorgusuna eklenir.
    İşlem tamamlandıktan sonra ilgili cache temizlenir.
    """
    # permission_classes = [IsAuthenticated, HasBOMProductAccess]

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            logger.warning("Canlı veri çekme işlemi için token bulunamadı.")
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        # Query parametresi olarak gelen item_code'i alıyoruz.
        item_code = request.query_params.get('item_code', None)
        logger.debug("Fetch view: item_code parametresi: %s", item_code)

        try:
            logger.info("SAP HANA'dan canlı BOMComponent verileri çekiliyor...")
            with transaction.atomic():
                updated_components = update_components_from_hana(token, item_code=item_code)
                if not updated_components:
                    logger.info("SAP HANA'dan boş veri döndü.")
                    return Response({"message": "SAP HANA'dan boş veri döndü."}, status=status.HTTP_200_OK)
                # Güncellenen veriler cache'den temizleniyor.
                cache.delete('bom_components')
                serializer = BOMComponentSerializer(updated_components, many=True)
                logger.info("Güncellenen bileşen sayısı: %d", len(updated_components))
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("BOMComponent canlı veri çekimi sırasında hata oluştu.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BOMComponentLastUpdatedView(APIView):
    """
    Yerel veritabanındaki BOMComponent kayıtlarının en son güncelleme tarihini döner.
    Bu, sistemdeki son değişiklik zamanını takip etmek için kullanılır.
    """
    def get(self, request, *args, **kwargs):
        last_component = BOMComponent.objects.order_by('-updated_at').first()
        if last_component and last_component.updated_at:
            formatted_time = timezone.localtime(last_component.updated_at).strftime('%d.%m.%Y %H:%M')
            logger.debug("En son güncelleme tarihi: %s", formatted_time)
            return Response({"last_updated": formatted_time}, status=status.HTTP_200_OK)
        logger.debug("BOMComponent için güncelleme tarihi bilgisi bulunamadı.")
        return Response({"last_updated": "Veri yok"}, status=status.HTTP_200_OK)
