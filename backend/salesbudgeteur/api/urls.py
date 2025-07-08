# backend/salesbudgeteur/api/urls.py

from django.urls import path
from .views import (
    SalesBudgetEURListView,
    FetchHanaSalesBudgetEURView,
)
from .export_excel import ExportSalesBudgetEURXLSXView

app_name = "salesbudgeteur"

urlpatterns = [
    path("budgets-eur/", SalesBudgetEURListView.as_view(), name="budget-eur-list"),
    path("fetch-hana-data/", FetchHanaSalesBudgetEURView.as_view(), name="fetch-hana-eur-data"),
    path("export-xlsx/",  ExportSalesBudgetEURXLSXView.as_view(), name="export-eur-xlsx"),
]
