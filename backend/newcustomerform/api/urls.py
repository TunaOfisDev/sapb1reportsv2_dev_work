# backend/newcustomerform/api/urls.py
from django.urls import path
from .views import (
    NewCustomerFormCreateAPIView,
    NewCustomerFormListAPIView,
    NewCustomerFormRetrieveAPIView,
    UserNewCustomerFormListAPIView  # Yeni dashboard view'ini import ediyoruz.
)

app_name = 'newcustomerform'

urlpatterns = [
    path('', NewCustomerFormCreateAPIView.as_view(), name='create'),      # Yeni müşteri formu oluştur
    path('list/', NewCustomerFormListAPIView.as_view(), name='newcustomerform-list'),       # Tüm müşteri formlarını listele
    path('dashboard/', UserNewCustomerFormListAPIView.as_view(), name='dashboard'),  # Dashboard: Kullanıcının kendi formları
    path('<int:pk>/', NewCustomerFormRetrieveAPIView.as_view(), name='detail'),  # Belirli bir formu getir
]
