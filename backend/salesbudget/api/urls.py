# backend/salesbudget/api/urls.py
from django.urls import path
from .views import SalesBudgetView, FetchHanaSalesBudgetDataView
from .exportxlsx_view import ExportSalesBudgetXLSXView

app_name = 'salesbudget'

urlpatterns = [
    path('budgets/', SalesBudgetView.as_view(), name='budget-list-create'),
    path('fetch-hana-data/', FetchHanaSalesBudgetDataView.as_view(), name='fetch-hana-salesbudget'),
    path('export-xlsx/', ExportSalesBudgetXLSXView.as_view(), name='export-sales-budget-xlsx'),
]
