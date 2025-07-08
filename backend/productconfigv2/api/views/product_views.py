# backend/productconfigv2/api/views/product_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from ...models import ProductFamily, Product, SpecificationOption
from ..serializers import ProductFamilySerializer, ProductSerializer


class ProductFamilyViewSet(viewsets.ModelViewSet):
    queryset = ProductFamily.objects.all()
    serializer_class = ProductFamilySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['post'], url_path='configurator/preview')
    def configurator_preview(self, request, pk=None):
        selections = request.data.get('selections', {})
        return Response({'valid': True, 'price': '7500.00'}, status=status.HTTP_200_OK)


# ✅ BU kısmı sınıf DIŞINA TAŞIYORUZ
@api_view(["GET"])
def product_specifications_grouped(request, product_id):
    """
    Belirli bir ürüne ait özellik ve seçenekleri gruplanmış şekilde döner.
    Sadece o ürüne atanmış SpecificationOption kayıtları döner.
    Sıralama: spec_type__variant_order ASC, sonra istersen display_order.
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Ürün bulunamadı."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 1) Sorgu: Bu ürüne ait SpecificationOption kayıtlarını çekiyoruz.
    #    Ardından spec_type__variant_order ve display_order'a göre sıralıyoruz.
    spec_options_qs = (
        SpecificationOption.objects
        .filter(product=product)
        .select_related("spec_type", "option")
        .order_by("spec_type__variant_order", "display_order")  # <-- Sıralama
    )

    # 2) Gruplamak için sözlük hazırlıyoruz: { spec_id: {...}, ... }
    grouped_map = {}

    for item in spec_options_qs:
        spec_id = item.spec_type.id

        if spec_id not in grouped_map:
            grouped_map[spec_id] = {
                "id": spec_id,
                "name": item.spec_type.name,
                "is_required": item.spec_type.is_required,
                "allow_multiple": item.spec_type.allow_multiple,
                "variant_order": item.spec_type.variant_order,
                "options": []
            }

        # Her bir spec_option kaydının "option" nesnesini mapliyoruz
        grouped_map[spec_id]["options"].append({
            "id": item.option.id,
            "name": item.option.name,
            "variant_code": item.option.variant_code,
            "variant_description": item.option.variant_description,
            "price_delta": item.option.price_delta,
            "is_default": item.is_default,
        })

    # 3) grouped_map'i listeye dönüştürüp variant_order'a göre sıralayacağız
    grouped_list = list(grouped_map.values())
    grouped_list.sort(key=lambda x: x["variant_order"])  # variant_order ASC

    return Response(grouped_list, status=200)
