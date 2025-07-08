# path: backend/stockcardintegration/api/urls.py

from django.urls import path
from .views import (
    StockCardListView, StockCardDetailView, StockCardSyncTriggerView,
    BulkStockCardCreateView, StockCardUpdateByCodeView
)
from .helptext_views import FieldHelpTextListView
from .views_sap import SAPLiveStockCardFetchView

app_name = "stockcardintegration"

urlpatterns = [
    path("stock-cards/", StockCardListView.as_view(), name="stock-card-list"),
    path("stock-cards/<int:pk>/", StockCardDetailView.as_view(), name="stock-card-detail"),
    path("stock-cards/<int:pk>/trigger-sync/", StockCardSyncTriggerView.as_view(), name="stock-card-sync"),
    path("stock-cards/bulk-create/", BulkStockCardCreateView.as_view(), name="stockcard-bulk-create"),
    path("stock-cards/code/<str:item_code>/", StockCardUpdateByCodeView.as_view(), name="stockcard-update-by-code"),

    # Yeni SAP canlı veri alma endpoint'i
    path("stock-cards/sap-live/<str:item_code>/", SAPLiveStockCardFetchView.as_view(), name="stockcard-sap-live-fetch"),

    # HelpText endpoint
    path("field-help-texts/", FieldHelpTextListView.as_view(), name="field-help-text-list"),
]
