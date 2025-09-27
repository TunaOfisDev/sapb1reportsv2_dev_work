# backend/salesorder/api/customersales_view.py
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models.customersalesorder import CustomerSalesOrder
from ..serializers import CustomerSalesOrderSerializer
from ..utilities.data_fetcher import fetch_hana_db_customersales
from django.utils import timezone

class CustomerSalesOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # 'customer_sales_orders_list' için bir cache anahtarı oluşturuluyor
        cache_key = 'customer_sales_orders_list'
        cache_time = settings.CACHE_TTL

        try:
            customer_sales_orders = cache.get(cache_key)
            if not customer_sales_orders:
                customer_sales_orders = CustomerSalesOrder.objects.all()
                serializer = CustomerSalesOrderSerializer(customer_sales_orders, many=True)
                cache.set(cache_key, serializer.data, cache_time)
                return Response(serializer.data)
            else:
                return Response(customer_sales_orders)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FetchHanaCustomerSalesDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        customersales_data = fetch_hana_db_customersales(token)

        if customersales_data:
            saved_objects = []
            errors = []
            for data in customersales_data:
                # Veri setinden gelen alanları modeldeki alan adlarıyla eşleştir
                mapped_data = {
                    'grup': data.get('Grup'),
                    'musteri_kod': data.get('MusteriKod'),
                    'musteri_ad': data.get('MusteriAd'),
                    'yil': data.get('Yil'),
                    'ocak': data.get('Ocak'),
                    'subat': data.get('Şubat'),
                    'mart': data.get('Mart'),
                    'nisan': data.get('Nisan'),
                    'mayis': data.get('Mayıs'),
                    'haziran': data.get('Haziran'),
                    'temmuz': data.get('Temmuz'),
                    'agustos': data.get('Ağustos'),
                    'eylul': data.get('Eylül'),
                    'ekim': data.get('Ekim'),
                    'kasim': data.get('Kasım'),
                    'aralik': data.get('Aralık'),
                    'yillik_toplam': data.get('YillikToplam'),
                }
                instance, _ = CustomerSalesOrder.objects.get_or_create(musteri_kod=mapped_data['musteri_kod'])
                serializer = CustomerSalesOrderSerializer(instance, data=mapped_data, partial=True)
                if serializer.is_valid():
                    saved_obj = serializer.save()
                    saved_objects.append(saved_obj)
                else:
                    errors.append(serializer.errors)

            if saved_objects:
                return Response({
                    'message': f'{len(saved_objects)} customer sales orders successfully fetched and saved.',
                    'errors': errors
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Some data could not be updated',
                    'errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Failed to fetch data from HANA DB'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LastUpdatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        last_updated_order = CustomerSalesOrder.objects.order_by('-updated_at').first()
        if last_updated_order:
            # İstanbul zaman dilimine göre ayarla
            last_updated_time = timezone.localtime(last_updated_order.updated_at, timezone=timezone.get_fixed_timezone(180))  # +3 saat için 180 dakika
            # İstenen formatı kullan
            formatted_time = last_updated_time.strftime('%d.%m.%Y %H:%M')
            return Response({"last_updated": formatted_time})
        else:
            return Response({"last_updated": "No data available"})
        

