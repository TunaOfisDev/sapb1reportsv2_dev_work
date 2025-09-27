# backend/salesbudget/api/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models.models import SalesBudget
from ..serializers import SalesBudgetSerializer
from ..utilities.data_fetcher import fetch_hana_db_data

class SalesBudgetView(generics.ListCreateAPIView):
    queryset = SalesBudget.objects.all()
    serializer_class = SalesBudgetSerializer
    permission_classes = [IsAuthenticated]

class FetchHanaSalesBudgetDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1]
        sales_budget_data = fetch_hana_db_data(token)

        if sales_budget_data:
            saved_objects = []
            errors = []
            for data in sales_budget_data:
                mapped_data = {
                    'satici': data.get('Satici'),
                    'toplam_gercek': data.get('Toplam_Gercek'),
                    'toplam_hedef': data.get('Toplam_Hedef'),
                    'oca_gercek': data.get('Oca_Gercek'),
                    'oca_hedef': data.get('Oca_Hedef'),
                    'sub_gercek': data.get('Şub_Gercek'),
                    'sub_hedef': data.get('Şub_Hedef'),
                    'mar_gercek': data.get('Mar_Gercek'),
                    'mar_hedef': data.get('Mar_Hedef'),
                    'nis_gercek': data.get('Nis_Gercek'),
                    'nis_hedef': data.get('Nis_Hedef'),
                    'may_gercek': data.get('May_Gercek'),
                    'may_hedef': data.get('May_Hedef'),
                    'haz_gercek': data.get('Haz_Gercek'),
                    'haz_hedef': data.get('Haz_Hedef'),
                    'tem_gercek': data.get('Tem_Gercek'),
                    'tem_hedef': data.get('Tem_Hedef'),
                    'agu_gercek': data.get('Ağu_Gercek'),
                    'agu_hedef': data.get('Ağu_Hedef'),
                    'eyl_gercek': data.get('Eyl_Gercek'),
                    'eyl_hedef': data.get('Eyl_Hedef'),
                    'eki_gercek': data.get('Eki_Gercek'),
                    'eki_hedef': data.get('Eki_Hedef'),
                    'kas_gercek': data.get('Kas_Gercek'),
                    'kas_hedef': data.get('Kas_Hedef'),
                    'ara_gercek': data.get('Ara_Gercek'),
                    'ara_hedef': data.get('Ara_Hedef'),
                }
                instance, created = SalesBudget.objects.update_or_create(
                    satici=mapped_data['satici'],
                    defaults=mapped_data
                )
                if created or instance.pk:
                    saved_objects.append(instance)
                else:
                    errors.append({'satici': mapped_data['satici'], 'error': 'Kayıt oluşturulamadı veya güncellenemedi.'})

            if saved_objects:
                return Response({
                    'message': f'{len(saved_objects)} sales budget records successfully fetched and saved.',
                    'errors': errors
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Some data could not be updated or created',
                    'errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Failed to fetch data from HANA DB'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
