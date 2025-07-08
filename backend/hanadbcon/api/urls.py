# URL'ye göre view bağlama
from django.urls import path
from .views import SQLQueryView, SQLQueryListView

urlpatterns = [
    path('query/<str:query_name>/', SQLQueryView.as_view(), name='sqlquery-detail-hana'),
    path('queries/', SQLQueryListView.as_view(), name='sqlquery-list-hana'),
]
