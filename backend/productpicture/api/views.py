# backend/productpicture/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models.productpicture_models import Product
from ..serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from ..utilities.data_fetcher import fetch_hana_db_data
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings


class APIRootView(APIView):
    def get(self, request, format=None):
        api_urls = {
            'Fetch Products': request.build_absolute_uri(reverse('productpicture:product-list')),
            'Fetch HANA Data': request.build_absolute_uri(reverse('productpicture:fetch-hana-data')),
        }
        return Response(api_urls)

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Token'ı header'dan al
        token = request.headers.get('Authorization').split(' ')[1]
        data = fetch_hana_db_data(token)  # Token'ı sağla
        if data:
            Product.update_from_api(data)
            return Response({'message': 'Data successfully fetched and saved to the local database'})
        else:
            return Response({'error': 'Data could not be retrieved from HANA DB'}, status=500)

class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        cache_key = 'products_list'
        cache_time = settings.CACHE_TTL  # settings.py dosyasından CACHE_TTL'yi kullan

        products = cache.get(cache_key)
        if not products:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            cache.set(cache_key, serializer.data, cache_time)
            return Response(serializer.data)
        else:
            return Response(products)


