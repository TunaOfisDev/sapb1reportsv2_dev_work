# path: backend/stockcardintegration/api/productpricelist_views.py
"""
ProductPriceList API – tam CRUD + canlı veri çekme endpoint’leri içerir.

- /product-price-list/         : CRUD işlemleri
- /product-price-list/refresh/ : Manuel senkron (POST)
- /product-price-list/live/    : Anlık veri (async Celery tetiklenir, mevcut veri döner)
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from stockcardintegration.models.productpricelist_models import ProductPriceList
from .serializers import ProductPriceListSerializer
from stockcardintegration.tasks.sync_price_list import sync_price_list
from stockcardintegration.services.productpricelist_services import (
    sync_price_list_if_needed,
    _is_recent_sync,
)

# ────────────────────────────────────────────────────────────────
# 1) Tam CRUD + refresh action
# ────────────────────────────────────────────────────────────────
class ProductPriceListViewSet(viewsets.ModelViewSet):
    """
    /product-price-list/ için tam CRUD işlemleri + /refresh action’ı
    """
    queryset = ProductPriceList.objects.all()
    serializer_class = ProductPriceListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("price_list_name", "currency")
    search_fields = ("item_code", "item_name", "old_component_code")
    ordering_fields = ("item_code", "price")
    ordering = ("item_code",)

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        """
        POST /product-price-list/refresh/  ⇒ HANA’dan veriyi senkron çeker ve kaydeder.
        """
        try:
            count = sync_price_list_if_needed()
            return Response({"updated": count}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ────────────────────────────────────────────────────────────────
# 2) Her zaman güncel veri – async Celery tetiklenir
# ────────────────────────────────────────────────────────────────
class LivePriceListView(APIView):
    """
    GET /product-price-list/live/  ⇒ Mevcut veriyi döner, TTL süresi aşıldıysa arka planda Celery çalışır.
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        if not _is_recent_sync():
            sync_price_list.delay()

        qs = ProductPriceList.objects.all()
        serializer = ProductPriceListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
