# path: backend/stockcardintegration/api/urls.py

from django.urls import path
from .views import (
    StockCardListView, StockCardDetailView, StockCardSyncTriggerView,
    BulkStockCardCreateView, StockCardUpdateByCodeView
)
from .helptext_views import FieldHelpTextListView
from .views_sap import SAPLiveStockCardFetchView
from .productpricelist_views import ProductPriceListViewSet, LivePriceListView
from rest_framework.routers import DefaultRouter

app_name = "stockcardintegration"

router = DefaultRouter()
router.register("product-price-list", ProductPriceListViewSet, basename="product-price-list")

urlpatterns = [
    # StockCard klasik endpoint'leri
    path("stock-cards/", StockCardListView.as_view(), name="stock-card-list"),
    path("stock-cards/<int:pk>/", StockCardDetailView.as_view(), name="stock-card-detail"),
    path("stock-cards/<int:pk>/trigger-sync/", StockCardSyncTriggerView.as_view(), name="stock-card-sync"),
    path("stock-cards/bulk-create/", BulkStockCardCreateView.as_view(), name="stockcard-bulk-create"),
    path("stock-cards/code/<str:item_code>/", StockCardUpdateByCodeView.as_view(), name="stockcard-update-by-code"),
    path("stock-cards/sap-live/<str:item_code>/", SAPLiveStockCardFetchView.as_view(), name="stockcard-sap-live-fetch"),

    # Yardım metinleri
    path("field-help-texts/", FieldHelpTextListView.as_view(), name="field-help-text-list"),

    # Ürün fiyat listesi – canlı veri (async Celery tetikleme)
    path("product-price-list/live/", LivePriceListView.as_view(), name="product-price-list-live"),
]

# DRF router'dan gelen tüm /product-price-list/... yolları burada ekleniyor
urlpatterns += router.urls
