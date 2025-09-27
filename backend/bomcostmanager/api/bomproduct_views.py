# backend/bomcostmanager/api/bomproduct_views.py

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from ..models.bomproduct_models import BOMProduct
from ..api.serializers import BOMProductSerializer
from ..services.bomproduct_service import update_products_from_hana
# from bomcostmanager.permissions import HasBOMProductAccess  # Özel yetkilendirme

logger = logging.getLogger(__name__)

class BOMProductListView(APIView):
    """
    Yerel veritabanında saklanan tüm BOMProduct kayıtlarını listeler.
    30 saniyelik cache süresi ile performanslı veri sunumu sağlanır.
    """
    # permission_classes = [IsAuthenticated, HasBOMProductAccess]

    @method_decorator(cache_page(30))
    def get(self, request, *args, **kwargs):
        cached_data = cache.get('bom_products')
        if cached_data:
            logger.debug("Cache'den BOMProduct verisi getirildi, kayıt sayısı: %d", len(cached_data))
            return Response(cached_data, status=status.HTTP_200_OK)

        products = BOMProduct.objects.all()
        serializer = BOMProductSerializer(products, many=True)
        cache.set('bom_products', serializer.data, timeout=30)
        logger.debug("BOMProduct listesi sorgulandı ve cache'e kaydedildi, kayıt sayısı: %d", len(serializer.data))
        return Response(serializer.data, status=status.HTTP_200_OK)


class BOMProductFetchView(APIView):
    """
    SAP HANA’dan canlı BOMProduct verilerini çeker ve yerel veritabanını günceller.
    Güncelleme işlemi sonrasında ilgili cache temizlenir.
    """
    # permission_classes = [IsAuthenticated, HasBOMProductAccess]

    @method_decorator(cache_page(30))
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            logger.warning("Canlı veri çekme işlemi için token bulunamadı.")
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            logger.info("SAP HANA'dan canlı BOMProduct verileri çekiliyor...")
            with transaction.atomic():
                updated_products = update_products_from_hana(token)
                if not updated_products:
                    logger.info("SAP HANA'dan boş veri döndü.")
                    return Response({"message": "SAP HANA'dan boş veri döndü."}, status=status.HTTP_200_OK)
                # Güncellenen veriler için cache temizleniyor.
                cache.delete('bom_products')
                serializer = BOMProductSerializer(updated_products, many=True)
                logger.info("Güncellenen ürün sayısı: %d", len(updated_products))
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("BOMProduct canlı veri çekimi sırasında hata oluştu.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BOMProductLastUpdatedView(APIView):
    """
    Yerel veritabanındaki BOMProduct kayıtlarından en son veri çekilme zamanını döner.
    """
    def get(self, request, *args, **kwargs):
        last_fetch = BOMProduct.objects.order_by('-last_fetched_at').first()
        if last_fetch and last_fetch.last_fetched_at:
            formatted_time = timezone.localtime(last_fetch.last_fetched_at).strftime('%d.%m.%Y %H:%M')
            logger.debug("En son veri çekilme zamanı: %s", formatted_time)
            return Response({"last_fetched_at": formatted_time}, status=status.HTTP_200_OK)
        logger.debug("BOMProduct için veri çekilme zamanı bulunamadı.")
        return Response({"last_fetched_at": "Veri yok"}, status=status.HTTP_200_OK)


class BOMProductDetailView(APIView):
    """
    Belirli bir ürün koduna sahip BOMProduct kaydının detaylarını döner.
    """
    def get(self, request, item_code, *args, **kwargs):
        try:
            product = BOMProduct.objects.get(item_code=item_code)
            serializer = BOMProductSerializer(product)
            logger.debug("Detay görüntüleme: %s", item_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BOMProduct.DoesNotExist:
            logger.warning("Ürün bulunamadı: %s", item_code)
            return Response({"error": f"Ürün kodu {item_code} bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
