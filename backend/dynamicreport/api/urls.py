# backend\dynamicreport\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sql-queries', views.SqlQueryViewSet)
router.register(r'dynamic-tables', views.DynamicTableViewSet)
router.register(r'manual-headers', views.DynamicHeadersViewSet)

# Adding URL pattern for check_column_types custom action
custom_urlpatterns = [
    path('dynamic-tables/<str:table_name>/check_column_types/', views.DynamicTableViewSet.as_view({'post': 'check_column_types'}), name='check_column_types_by_name'),
    path('test-and-generate-report/', views.test_and_generate_report, name='test_and_generate_report'),  # Yeni eklenen URL
    path('get-sql-query-list/', views.get_sql_query_list, name='get_sql_query_list')  # Yeni eklenen URL
]

urlpatterns = [
    path('', include(router.urls)),
    path('fetch_instant_data/by_name/<str:table_name>/', views.fetch_instant_data_by_name),
    path('sql-queries/by_id/<int:pk>/', views.sql_query_detail_by_id),
    path('sql-queries/by_name/<str:table_name>/', views.sql_query_detail_by_name), 
    path('sql-table-list/', views.sql_table_list),
    path('dynamic-tables/by_id/<int:pk>/', views.DynamicTableViewSet.as_view({'get': 'retrieve'})),  
    path('dynamic-tables/by_name/<str:table_name>/', views.DynamicTableViewSet.as_view({'get': 'retrieve_by_name'})),
    path('manual-headers/by_id/<int:pk>/', views.dynamic_headers_detail),
    path('manual-headers/by_name/<str:table_name>/', views.DynamicHeadersByTable.as_view()),  
    path('dynamic-tables/fetch_local_data_with_alignment/<str:table_name>/', views.DynamicTableViewSet.as_view({'get': 'fetch_local_data_with_alignment'})),
    
] + custom_urlpatterns # append custom urlpatterns
