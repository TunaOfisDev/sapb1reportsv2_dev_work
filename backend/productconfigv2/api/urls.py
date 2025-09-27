# productconfigv2/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductFamilyViewSet, ProductViewSet,
    SpecificationTypeViewSet, SpecOptionViewSet,
    ProductSpecificationViewSet, SpecificationOptionViewSet,
    VariantViewSet, RuleViewSet, product_specifications_grouped,
    sap_test_view # Test view'ını import ettiğimizden emin olalım
)

router = DefaultRouter()
router.register(r"product-families", ProductFamilyViewSet)
router.register(r"products", ProductViewSet)
router.register(r"specification-types", SpecificationTypeViewSet)
router.register(r"spec-options", SpecOptionViewSet)
router.register(r"product-specifications", ProductSpecificationViewSet)
router.register(r"specification-options", SpecificationOptionViewSet)
router.register(r"variants", VariantViewSet)
router.register(r"rules", RuleViewSet)

# GÜNCELLEME: URL listesinin sırası değiştirildi.
urlpatterns = [
    # Adım 1: Özel ve daha spesifik URL'leri router'dan ÖNCE tanımla.
    path("products/<int:product_id>/specifications-grouped/", product_specifications_grouped),
    path("variants/sap-test/", sap_test_view, name="sap-test-view"),
    
    # Adım 2: Daha genel olan ve <pk> gibi değişkenler içeren router URL'lerini sona ekle.
    path("", include(router.urls)),
]