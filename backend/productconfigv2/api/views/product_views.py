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
    Frontend'in konfigüratör ekranını oluşturması için gereken tüm veriyi sağlar.
    """
    try:
        # Adım 1: İlgili ürünü veritabanında bul.
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Ürün bulunamadı."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Adım 2: Bu ürüne bağlı olan tüm geçerli özellik-seçenek ilişkilerini
    # tek bir veritabanı sorgusu ile çek. Performans için .select_related() kullanılır.
    # Sonuçlar, özelliklerin gösterim sırasına göre sıralanır.
    spec_options_qs = (
        SpecificationOption.objects
        .filter(product=product, is_active=True)
        .select_related("spec_type", "option")
        .order_by("spec_type__variant_order", "display_order")
    )

    # Adım 3: Verileri gruplamak için boş bir dictionary (sözlük) oluştur.
    # Bu sözlüğün anahtarı özellik ID'si (spec_id), değeri ise özelliğin bilgileri olacak.
    grouped_map = {}

    # Adım 4: Veritabanından gelen her bir satır için döngü başlat ve grupla.
    for item in spec_options_qs:
        spec_id = item.spec_type.id

        # Eğer bu özellik (spec_type) ile ilk defa karşılaşıyorsak,
        # sözlüğe bu özellik için yeni bir ana yapı oluştur.
        if spec_id not in grouped_map:
            grouped_map[spec_id] = {
                "id": spec_id,
                "name": item.spec_type.name,
                "is_required": item.spec_type.is_required,
                "allow_multiple": item.spec_type.allow_multiple,
                "variant_order": item.spec_type.variant_order,
                "options": []  # Bu özelliğe ait seçenekleri bu listeye ekleyeceğiz.
            }

        # Mevcut satırdaki seçeneğin (option) bilgilerini al ve ilgili özelliğin
        # "options" listesine ekle.
        grouped_map[spec_id]["options"].append({
            "id": item.option.id,
            "name": item.option.name,
            "variant_code": item.option.variant_code,
            "variant_description": item.option.variant_description,
            "reference_code": item.option.reference_code, # YENİ ALAN
            "price_delta": item.option.price_delta,
            "is_default": item.is_default,
        })

    # Adım 5: Gruplanmış sözlüğü, frontend'in beklediği liste formatına çevir.
    grouped_list = list(grouped_map.values())
    
    # Not: Sorguda sıralama yaptığımız için bu satır aslında gerekmeyebilir,
    # ancak garantici olmak adına grupların da sıralı olduğundan emin oluyoruz.
    grouped_list.sort(key=lambda x: x["variant_order"])

    # Adım 6: Hazırlanan listeyi API yanıtı olarak frontend'e gönder.
    return Response(grouped_list, status=status.HTTP_200_OK)
