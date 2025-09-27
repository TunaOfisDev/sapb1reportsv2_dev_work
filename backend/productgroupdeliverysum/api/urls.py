# backend/productgroupdeliverysum/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliverySummaryViewSet

app_name = 'productgroupdeliverysum'

# DefaultRouter'ı kullanarak viewset'i kaydediyoruz
router = DefaultRouter()
router.register(r'', DeliverySummaryViewSet, basename='delivery-summary')

urlpatterns = [
    # Router ile oluşturulan otomatik endpoint'ler
    path('', include(router.urls)),
    
    # Ekstra aksiyonlar için manuel path'ler
    path('fetch-hana/', 
         DeliverySummaryViewSet.as_view({'get': 'fetch_hana_data'}), 
         name='fetch-hana-data'),
    
    path('local-data/', 
         DeliverySummaryViewSet.as_view({'get': 'get_local_data'}), 
         name='local-data'),
    
    # Yıl karşılaştırma endpoint'i
    path('year-comparison/<int:year>/', 
         DeliverySummaryViewSet.as_view({'get': 'get_year_comparison'}), 
         name='year-comparison'),
]