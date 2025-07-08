# productconfigv2/api/views/variant_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import Variant, Product
from ..serializers import VariantSerializer
from ...services.variant_service import (
    create_variant_with_selections,
    preview_variant,
)
from ...services.rule_engine import is_valid_combination


class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

    @action(detail=False, methods=["post"])
    def create_from_selection(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"detail": "product_id gereklidir"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Belirtilen ID ile ürün bulunamadı"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        selections = request.data.get("selections", {})
        user = request.user if request.user.is_authenticated else None

        if not is_valid_combination(product_id, selections):
            return Response(
                {"detail": "Geçersiz kombinasyon!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            variant = create_variant_with_selections(product_id, selections, user)
            serializer = self.get_serializer(variant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=["post"])
    def preview(self, request):
        product_id = request.data.get("product_id")
        selections = request.data.get("selections", {})
        data = preview_variant(product_id, selections)
        return Response(data, status=status.HTTP_200_OK)
