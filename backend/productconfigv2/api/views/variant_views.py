# backend/productconfigv2/api/views/variant_views.py

from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from ...models import Variant, Product
from ..serializers import VariantSerializer
from ...services.variant_service import (
    create_variant_with_selections,
    preview_variant,
    update_variant_price_from_sap
)
from ...services.sap_service_layer import get_price_by_item_code 
from ...services.rule_engine import is_valid_combination
from ...filters import VariantFilter # Yeni filter sınıfımızı import ediyoruz


class VariantViewSet(viewsets.ModelViewSet):
    """
    Oluşturulmuş varyantları listelemek, oluşturmak ve yönetmek için API endpoint'i.
    """
    serializer_class = VariantSerializer
    
    # GÜNCELLEME: Performans için select_related eklendi.
    queryset = Variant.objects.select_related('product', 'created_by').order_by('-created_at')
    
    # GÜNCELLEME: Filtreleme, arama ve sıralama backend'leri eklendi.
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VariantFilter
    search_fields = ['project_name', 'reference_code', 'new_variant_code', 'new_variant_description']
    ordering_fields = ['created_at', 'project_name', 'total_price']

    
    @action(detail=False, methods=["post"], url_path="create_from_selection")
    def create_from_selection(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"detail": "product_id gereklidir"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Belirtilen ID ile ürün bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

        selections = request.data.get("selections", {})
        project_name = request.data.get("project_name")
        user = request.user if request.user.is_authenticated else None

        if not project_name or not project_name.strip():
            return Response({"detail": "Proje Adı alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        if not is_valid_combination(product.family.id, selections):
            return Response({"detail": "Geçersiz kombinasyon! Lütfen seçiminizi kontrol edin."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant = create_variant_with_selections(product_id, selections, project_name.strip(), user)
            serializer = self.get_serializer(variant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def preview(self, request):
        product_id = request.data.get("product_id")
        selections = request.data.get("selections", {})
        
        if not product_id:
            return Response({"detail": "product_id gereklidir"}, status=status.HTTP_400_BAD_REQUEST)

        data = preview_variant(product_id, selections) 
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='update-price-from-sap')
    def update_price(self, request, pk=None):
        """Tek bir varyantın fiyatını SAP'den günceller."""
        if not pk:
            return Response({"detail": "Varyant ID'si gerekli."}, status=status.HTTP_400_BAD_REQUEST)

        success, message = update_variant_price_from_sap(variant_id=pk)

        if success:
            variant = self.get_object()
            serializer = self.get_serializer(variant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='get-sap-price')
    def get_sap_price(self, request):
        reference_code = request.query_params.get('reference_code', None)
        if not reference_code:
            return Response({"detail": "reference_code parametresi gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

        success, result = get_price_by_item_code(reference_code)

        if success:
            return Response({"price": result}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)

def sap_test_view(request):
    """SAP bağlantısını izole bir şekilde test eder."""
    test_code = "55.BW.16070.K0.E0.ALU" 
    success, result = get_price_by_item_code(test_code)

    if success:
        return JsonResponse({"status": "success", "item_code": test_code, "price": float(result)})
    else:
        return JsonResponse({"status": "error", "message": result}, status=500)