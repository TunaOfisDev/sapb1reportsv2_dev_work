# backend/customercollection/api/closinginvoice_view.py
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction as db_transaction
from ..models.models import CustomerCollection
from ..models.closinginvoice import ClosingInvoice
from loguru import logger

logger.add("logs/backend.log", rotation="1 MB")

class CustomerCollectionSimulation:
    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(lambda: {
            'borc': Decimal('0.00'), 
            'alacak': Decimal('0.00'),
            'cari_ad': '',
            'satici': '',
            'grup': '',
            'odemekosulu': ''
        }))

    def process_transactions(self):
        # Tüm işlemleri tarih sırasına göre işle
        for collection in CustomerCollection.objects.all().order_by('belge_tarih'):
            date = datetime.strptime(collection.belge_tarih, "%Y-%m-%d").date()
            year_month = date.strftime("%Y-%m")  # YYYY-MM formatı
            
            self.data[collection.cari_kod][year_month]['borc'] += collection.borc
            self.data[collection.cari_kod][year_month]['alacak'] += collection.alacak
            self.data[collection.cari_kod][year_month]['cari_ad'] = collection.cari_ad
            self.data[collection.cari_kod][year_month]['satici'] = collection.satici
            self.data[collection.cari_kod][year_month]['grup'] = collection.grup
            self.data[collection.cari_kod][year_month]['odemekosulu'] = collection.odemekosulu

    def generate_collection_list(self):
        try:
            collection_list = []
            current_date = datetime.now()
            
            # Son 4 ayı hesapla
            last_4_months = []
            temp_date = current_date
            
            for _ in range(4):
                last_4_months.append(temp_date.replace(day=1))
                if temp_date.month == 1:
                    temp_date = temp_date.replace(year=temp_date.year-1, month=12, day=1)
                else:
                    temp_date = temp_date.replace(month=temp_date.month-1, day=1)

            # YYYY-MM formatında son 4 ay
            last_4_months_keys = [date.strftime("%Y-%m") for date in last_4_months]
            last_4_months_keys.reverse()  # Eskiden yeniye sırala

            for cari_kod, months in self.data.items():
                # 1. Önce toplam alacak hesaplanır
                total_alacak = sum(month_data['alacak'] for month_data in months.values())
                remaining_alacak = total_alacak  # Kalan alacak
                
                # Ayları kronolojik sırala
                sorted_months = sorted(months.keys())
                
                # Aylık bakiyeleri sıfırla
                monthly_balances = {month: Decimal('0.00') for month in last_4_months_keys}
                oncesi_balance = Decimal('0.00')
                
                # 2. En eski tarihten başlayarak kapama yap
                for month in sorted_months:
                    current_borc = months[month]['borc']
                    
                    # 3. Her ay için kalan alacak ile borç karşılaştırılır
                    if remaining_alacak >= current_borc:
                        # Alacak borcu tamamen kapatıyor
                        remaining_alacak -= current_borc
                    else:
                        # 4. Kalan borç varsa ilgili aya yazılır
                        remaining_borc = current_borc - remaining_alacak
                        remaining_alacak = Decimal('0.00')
                        
                        # 5. Son 4 aydan önceki borçlar "öncesi" bakiyesine yazılır
                        if month in last_4_months_keys:
                            monthly_balances[month] = remaining_borc
                        else:
                            oncesi_balance += remaining_borc

                current_balance = oncesi_balance + sum(monthly_balances.values())
                customer_info = next(iter(months.values()))

                collection_list.append({
                    'cari_kod': cari_kod,
                    'cari_ad': customer_info['cari_ad'],
                    'satici': customer_info['satici'],
                    'grup': customer_info['grup'],
                    'odemekosulu': customer_info['odemekosulu'],
                    'current_balance': float(current_balance),
                    'monthly_balances': {
                        'oncesi': float(oncesi_balance),
                        **{k: float(v) for k, v in monthly_balances.items()}
                    }
                })

            return collection_list

        except Exception as e:
            logger.error(f"Error in generate_collection_list: {str(e)}")
            raise

class CustomerCollectionSimulationView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            simulation = CustomerCollectionSimulation()
            simulation.process_transactions()
            collection_list = simulation.generate_collection_list()

            if collection_list:
                with db_transaction.atomic():
                    updated_collection_list = []
                    for item in collection_list:
                        closing_invoice, created = ClosingInvoice.objects.update_or_create(
                            cari_kod=item['cari_kod'],
                            defaults={
                                'current_balance': item['current_balance'],
                                'monthly_balances': item['monthly_balances'],
                                'cari_ad': item['cari_ad'],
                                'satici': item['satici'],
                                'grup': item['grup'],
                                'odemekosulu': item['odemekosulu']
                            }
                        )
                        updated_collection_list.append({
                            'cari_kod': closing_invoice.cari_kod,
                            'cari_ad': closing_invoice.cari_ad,
                            'satici': closing_invoice.satici,
                            'grup': closing_invoice.grup,
                            'current_balance': closing_invoice.current_balance,
                            'monthly_balances': closing_invoice.monthly_balances,
                            'odemekosulu': closing_invoice.odemekosulu
                        })
                    return JsonResponse(updated_collection_list, safe=False)
            else:
                return Response({'message': 'Veri bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Error in CustomerCollectionSimulationView: {str(e)}")
            return Response({
                'error': 'İşlem sırasında bir hata oluştu.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)