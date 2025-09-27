# backend/report_orchestrator/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from report_orchestrator.api.views.api_report_view import (
    APIReportViewSet,
    ReportSummaryView,
    RunReportExportView,
)
from report_orchestrator.api.views.sofitel_balance_report_view import SofitelBalanceReportView
from report_orchestrator.api.views.sofitel_supplier_balance_report_view import SofitelSupplierBalanceReportView

router = DefaultRouter()
router.register(r'reports', APIReportViewSet, basename='api-reports')

urlpatterns = [
    path('', include(router.urls)),

    # Sofitel Müşteri Raporu – Pasif JSON çıktısı
    path('sofitel-balance/', SofitelBalanceReportView.as_view(), name='sofitel-balance-report'),

    # ✅ Yeni: Sofitel Tedarikçi Raporu
    path('sofitel-supplier-balance/', SofitelSupplierBalanceReportView.as_view(), name='sofitel-supplier-balance-report'),

    # Diğer Ortak Rapor API'leri
    path('reports/summary/', ReportSummaryView.as_view(), name='report-summary'),
    path('reports/run_report/', RunReportExportView.as_view(), name='report-export'),
]
