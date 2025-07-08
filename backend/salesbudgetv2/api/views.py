# backend/salesbudget/api/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models.models import SalesBudgetv2
from ..serializers import SalesBudgetSerializer
from ..utilities.data_fetcher import fetch_hana_db_data
from django.db import transaction

class SalesBudgetView(generics.ListCreateAPIView):
    queryset = SalesBudgetv2.objects.all()
    serializer_class = SalesBudgetSerializer
    permission_classes = [IsAuthenticated]

class FetchHanaSalesBudgetDataView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1]
        sales_budget_data = fetch_hana_db_data(token)
        
        if sales_budget_data:
            try:
                with transaction.atomic():
                    # Tüm mevcut kayıtları sil
                    SalesBudgetv2.objects.all().delete()
                    
                    # Yeni verileri kaydet
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
                        
                        try:
                            instance = SalesBudgetv2.objects.create(**mapped_data)
                            saved_objects.append(instance)
                        except Exception as e:
                            errors.append({
                                'satici': mapped_data['satici'], 
                                'error': f'Kayıt oluşturulamadı: {str(e)}'
                            })
                    
                    # İsteğe bağlı: Burada özet hesaplamalarını yapabilirsiniz
                    # calculate_summaries()
                    
                    if saved_objects:
                        return Response({
                            'message': f'Tüm eski veriler silindi. {len(saved_objects)} yeni satış bütçesi kaydı başarıyla kaydedildi.',
                            'errors': errors
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'error': 'Hiçbir veri kaydedilemedi',
                            'errors': errors
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                return Response({
                    'error': f'Veritabanı işlemi sırasında hata oluştu: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'error': 'HANA DB\'den veri alınamadı'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)