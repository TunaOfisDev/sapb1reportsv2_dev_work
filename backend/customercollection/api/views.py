# backend/customercollection/api/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from ..models.models import CustomerCollection
from ..serializers import CustomerCollectionSerializer
from ..utilities.data_fetcher import fetch_hana_db_data
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class CustomerCollectionView(generics.ListCreateAPIView):
    queryset = CustomerCollection.objects.all()
    serializer_class = CustomerCollectionSerializer
    permission_classes = [IsAuthenticated]


class FetchHanaCustomerCollectionDataView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(30))  # 30 saniye boyunca cachele
    def get(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        cache_key = f"customer_collection_data_{token}"  # Cache için benzersiz bir anahtar
        customer_collection_data = cache.get(cache_key)  # Cache'den veri çek

        if customer_collection_data is None:
            customer_collection_data = fetch_hana_db_data(token)
            if not customer_collection_data:
                return Response({
                    'error': 'Failed to fetch data from HANA DB or no new data found.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            cache.set(cache_key, customer_collection_data, timeout=30)  # Veriyi 30 saniyeliğine cache'e kaydet

        try:
            with transaction.atomic():
                CustomerCollection.objects.all().delete()  # Mevcut tüm kayıtları sil
                for data in customer_collection_data:  # Yeni verileri kaydet
                    CustomerCollection.objects.create(
                        belge_no=data['BELGE_NO'],
                        cari_kod=data['CARI_KOD'],
                        cari_ad=data['CARI_AD'],
                        satici=data['SATICI'],
                        grup=data['GRUP'],
                        belge_tarih=data['BELGE_TARIH'],
                        vade_tarih=data['VADE_TARIH'],
                        odemekod=data['ODEMEKOD'],
                        odemekosulu=data['ODEMEKOSULU'],
                        borc=data['BORC'],
                        alacak=data['ALACAK']
                    )

            return Response({'message': 'Veri başarıyla çekildi ve yenilendi.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'Veri güncelleme işlemi sırasında bir hata oluştu.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LastUpdatedCustomerCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        last_updated_collection = CustomerCollection.objects.order_by('-updated_at').first()
        
        if last_updated_collection:
            # Zamanı, kullanıcının bulunduğu zaman dilimine göre formatla
            last_updated_time = timezone.localtime(last_updated_collection.updated_at)
            formatted_time = last_updated_time.strftime('%d.%m.%Y %H:%M')
            return Response({"last_updated": formatted_time})
        else:
            return Response({"last_updated": "Veri yok"})
