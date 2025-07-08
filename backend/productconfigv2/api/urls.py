# productconfigv2/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductFamilyViewSet, ProductViewSet,
    SpecificationTypeViewSet, SpecOptionViewSet,
    ProductSpecificationViewSet, SpecificationOptionViewSet,
    VariantViewSet, RuleViewSet, product_specifications_grouped
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

urlpatterns = [
    path("", include(router.urls)),
    path("products/<int:product_id>/specifications-grouped/", product_specifications_grouped),
]
