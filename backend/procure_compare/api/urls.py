# File: procure_compare/api/urls.py

from django.urls import path
from procure_compare.api import views
from procure_compare.api.views import (
     SyncProcureCompareFromHANAView, 
     approval_action, ApprovalHistoryView,
     ApprovalHistoryGroupedView, ItemPurchaseHistoryView

     )

app_name = 'procure_compare'

urlpatterns = [
    path("orders/", views.PurchaseOrderListView.as_view(), name="purchase-orders"),
    path("quotes/", views.PurchaseQuoteListView.as_view(), name="purchase-quotes"),
    path("comparisons/", views.PurchaseComparisonListView.as_view(), name="purchase-comparisons"),
    path("sync-from-hana/", SyncProcureCompareFromHANAView.as_view(), name="sync-from-hana"), 
    path('approval-action/', approval_action, name='approval_action'),
    path("approval-history/", ApprovalHistoryView.as_view(), name="approval-history"),
    path("approval-history-grouped/", ApprovalHistoryGroupedView.as_view(), name="approval-history-grouped"),
    path('item-purchase-history/', ItemPurchaseHistoryView.as_view(), name='item-purchase-history'),

]


