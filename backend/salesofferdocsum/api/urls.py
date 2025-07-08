# backend/salesofferdocsum/api/urls.py
from django.urls import path
from .views import SalesOfferDetailListView, FetchHanaDataView
from .docsum_views import DocumentSummaryListView, DocumentSummaryDocView
from .salesofferdetaildoc import SalesOfferDetailDocView
from .datefilter_views import DateFilterView  
from .pivottables.customermonthlysummary import CustomerMonthlySummaryView 
from .pivottables.monthlysummary import MonthlySummaryView
from .pivottables.sellerMonthlysummary import SellerMonthlySummaryView
from .pivottablesv2.yearbasedmonthlysummary import YearBasedMonthlySummaryView  # type: ignore
from .pivottablesv2.yearlymonthlysummarybycustomer import YearlyMonthlySummaryByCustomerView  # type: ignore
from .pivottablesv2.yearlymonthlysummarybyvendor import YearlyMonthlySummaryByVendorView  # type: ignore

app_name = 'salesofferdocsum'

urlpatterns = [
    path('sales-offer-details/', SalesOfferDetailListView.as_view(), name='sales-offer-details-list'),
    path('fetch-hana-data/', FetchHanaDataView.as_view(), name='fetch-hana-salesoffer'),
    path('sales-offer-detail/<str:belge_no>/', SalesOfferDetailDocView.as_view(), name='sales-offer-detail-doc'),
    path('document-summaries/', DocumentSummaryListView.as_view(), name='document-summaries-list'),
    path('document-summary/<str:belge_no>/', DocumentSummaryDocView.as_view(), name='document-summary-doc'),
    path('date-filter/', DateFilterView.as_view(), name='date-filter'),  
    # pivottables
    path('customer-monthly-summary/', CustomerMonthlySummaryView.as_view(), name='customer-monthly-summary'), 
    path('monthly-summary/', MonthlySummaryView.as_view(), name='monthly-summary'),
    path('seller-monthly-summary/', SellerMonthlySummaryView.as_view(), name='seller-monthly-summary'),
    # pivottablesv2
    path('year-based-monthly-summary/', YearBasedMonthlySummaryView.as_view(), name='year-based-monthly-summary'),
    path('yearly-monthly-summary-by-customer/', YearlyMonthlySummaryByCustomerView.as_view(), name='yearly-monthly-summary-by-customer'),
    path('yearly-monthly-summary-by-vendor/', YearlyMonthlySummaryByVendorView.as_view(), name='yearly-monthly-summary-by-vendor'),

]
