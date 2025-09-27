# backend/tunainssupplierpayment/api/views.py
from datetime import datetime
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from ..models.models import SupplierPayment
from ..serializers import SupplierPaymentSerializer  
from ..api.closinginvoice_view import SupplierPaymentSimulation
from ..utilities.data_fetcher import fetch_hana_db_data
from loguru import logger
import time

class SupplierPaymentView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierPaymentSerializer

    def get_queryset(self):
        """Optimize edilmiş queryset"""
        queryset = SupplierPayment.objects.all()
        
        # Filtreler için query params kontrol et
        cari_kod = self.request.query_params.get('cari_kod', None)
        is_buffer = self.request.query_params.get('is_buffer', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if cari_kod:
            queryset = queryset.filter(cari_kod=cari_kod)
        if is_buffer is not None:
            queryset = queryset.filter(is_buffer=is_buffer.lower() == 'true')
        if date_from:
            queryset = queryset.filter(belge_tarih__gte=date_from)
        if date_to:
            queryset = queryset.filter(belge_tarih__lte=date_to)

        return queryset.select_related()

class BaseHanaDataView(APIView):
    """Temel HANA veri işleme sınıfı"""
    permission_classes = [IsAuthenticated]

    def process_hana_data(self, hana_data, is_first_run=False):
        """HANA verilerini işle"""
        current_year = str(datetime.now().year)
        bulk_create_data = []
        processed_count = {'new': 0, 'buffer': 0, 'skipped': 0}

        try:
            with transaction.atomic():
                # Güncel yıl verilerini sil
                if not is_first_run:
                    SupplierPayment.objects.filter(
                        Q(belge_tarih__startswith=current_year) & 
                        Q(is_buffer=False)
                    ).delete()

                for data in hana_data:
                    belge_tarih = data['BELGE_TARIH']
                    year = belge_tarih.split('-')[0]
                    is_buffer = year != current_year

                    # Buffer kontrolü
                    if is_buffer and not is_first_run:
                        exists = SupplierPayment.objects.filter(
                            belge_no=data['BELGE_NO'],
                            cari_kod=data['CARI_KOD'],
                            belge_tarih=belge_tarih,
                            is_buffer=True
                        ).exists()
                        
                        if exists:
                            processed_count['skipped'] += 1
                            continue

                    supplier_payment = SupplierPayment(
                        belge_no=data['BELGE_NO'],
                        cari_kod=data['CARI_KOD'],
                        cari_ad=data['CARI_AD'],
                        belge_tarih=belge_tarih,
                        iban=data['IBAN'],
                        odemekosulu=data['ODEMEKOSULU'],
                        borc=data['BORC'],
                        alacak=data['ALACAK'],
                        is_buffer=is_buffer
                    )
                    bulk_create_data.append(supplier_payment)

                    if is_buffer:
                        processed_count['buffer'] += 1
                    else:
                        processed_count['new'] += 1

                if bulk_create_data:
                    SupplierPayment.objects.bulk_create(
                        bulk_create_data,
                        batch_size=1000,
                        ignore_conflicts=True
                    )

                return processed_count

        except Exception as e:
            logger.error(f"Veri işleme hatası: {str(e)}")
            raise

class FetchHanaSupplierPaymentDataView(BaseHanaDataView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            hana_data = fetch_hana_db_data(token)

            if not hana_data:
                return Response({
                    'error': 'HANA DB\'den veri alınamadı veya yeni veri bulunamadı.'
                }, status=status.HTTP_404_NOT_FOUND)

            is_first_run = not SupplierPayment.objects.filter(is_buffer=True).exists()
            processed_count = self.process_hana_data(hana_data, is_first_run)

            return Response({
                'message': 'Veriler başarıyla güncellendi.',
                'details': processed_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"HANA veri çekme hatası: {str(e)}")
            return Response({
                'error': 'İşlem sırasında hata oluştu.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FetchHanaDbDataView(BaseHanaDataView):
    def get(self, request):
        try:
            # Token alınır
            token = request.headers.get('Authorization', '').split(' ')[1]
            
            # HANA DB'den veri çekilir
            hana_data = fetch_hana_db_data(token)
            
            if not hana_data:
                return Response({
                    'status': 'no_data',
                    'message': 'HANA veritabanında veri bulunamadı.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Timer başlat
            start_time = time.time()
            
            with transaction.atomic():
                # HANA verileri için benzersiz anahtar sözlüğü oluştur
                hana_records = {}
                for data in hana_data:
                    key = f"{data['BELGE_NO']}_{data['CARI_KOD']}_{data['BELGE_TARIH']}"
                    hana_records[key] = data
                
                # Yerel DB'deki mevcut kayıtları al
                # Bellek kullanımını azaltmak için yalnızca karşılaştırma için gereken alanları seç
                existing_records = {
                    f"{record[1]}_{record[2]}_{record[3]}": record[0]
                    for record in SupplierPayment.objects.values_list('id', 'belge_no', 'cari_kod', 'belge_tarih')
                }
                
                # Silinecek kayıtları belirle (HANA'da olmayan)
                to_delete_ids = [
                    record_id for key, record_id in existing_records.items()
                    if key not in hana_records
                ]
                
                # Eklenecek ve güncellenecek kayıtları hazırla
                current_year = str(datetime.now().year)
                to_create = []
                to_update = []
                
                for key, data in hana_records.items():
                    belge_tarih = data['BELGE_TARIH']
                    year = belge_tarih.split('-')[0]
                    is_buffer = year != current_year
                    
                    record_data = {
                        'belge_no': data['BELGE_NO'],
                        'cari_kod': data['CARI_KOD'],
                        'cari_ad': data['CARI_AD'],
                        'belge_tarih': belge_tarih,
                        'iban': data['IBAN'],
                        'odemekosulu': data['ODEMEKOSULU'],
                        'borc': data['BORC'],
                        'alacak': data['ALACAK'],
                        'is_buffer': is_buffer
                    }
                    
                    if key in existing_records:
                        # Güncelleme için ID ekle
                        record_data['id'] = existing_records[key]
                        to_update.append(record_data)
                    else:
                        to_create.append(SupplierPayment(**record_data))
                
                # Toplu işlemleri gerçekleştir
                if to_delete_ids:
                    deleted_count = SupplierPayment.objects.filter(id__in=to_delete_ids).delete()[0]
                else:
                    deleted_count = 0
                    
                # Bulk create (yeni kayıtlar)
                if to_create:
                    SupplierPayment.objects.bulk_create(to_create, batch_size=1000)
                
                # Bulk update (güncellenen kayıtlar)
                # Django 2.2+ için bulk_update kullanımı
                if to_update:
                    update_objects = []
                    for data in to_update:
                        record_id = data.pop('id')
                        obj = SupplierPayment(id=record_id, **data)
                        update_objects.append(obj)
                    
                    if update_objects:
                        # Güncellenecek alanları belirt
                        fields_to_update = ['cari_ad', 'iban', 'odemekosulu', 'borc', 'alacak', 'is_buffer']
                        SupplierPayment.objects.bulk_update(update_objects, fields_to_update, batch_size=1000)
                
                # Kapanış faturalarını güncelleme - API çağrısı yerine doğrudan fonksiyonu çağır
                from ..api.closinginvoice_view import SupplierPaymentSimulation
                simulation = SupplierPaymentSimulation()
                simulation.process_transactions()
                payment_list = simulation.generate_payment_list()
                
                # ClosingInvoice modeli için toplu güncelleme
                if payment_list:
                    from ..models.closinginvoice import ClosingInvoice
                    ClosingInvoice.objects.all().delete()  # Mevcut kapanış faturalarını temizle
                    
                    closing_invoices = []
                    for item in payment_list:
                        if float(item['current_balance']) == 0:
                            continue
                            
                        closing_invoice = ClosingInvoice(
                            cari_kod=item['cari_kod'],
                            cari_ad=item.get('cari_ad', 'Unknown'),
                            current_balance=item['current_balance'],
                            monthly_balances=item['monthly_balances']
                        )
                        closing_invoices.append(closing_invoice)
                    
                    if closing_invoices:
                        ClosingInvoice.objects.bulk_create(closing_invoices, batch_size=1000)
            
            # İşlem süresini hesapla
            elapsed_time = time.time() - start_time
            
            # Sonuçları döndür
            return Response({
                'status': 'success',
                'message': 'Veriler başarıyla güncellendi.',
                'details': {
                    'created': len(to_create),
                    'updated': len(to_update),
                    'deleted': deleted_count,
                    'total_processed': len(hana_data),
                    'process_time_seconds': round(elapsed_time, 2)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"HANA DB veri güncelleme hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Veriler güncellenirken bir hata oluştu.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            



class LastUpdatedSupplierPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Önce güncel yıl verilerini kontrol et
            current_year = str(datetime.now().year)
            last_updated_payment = SupplierPayment.objects.filter(
                belge_tarih__startswith=current_year,
                is_buffer=False
            ).order_by('-updated_at').first()

            # Güncel veri yoksa buffer verilerini kontrol et
            if not last_updated_payment:
                last_updated_payment = SupplierPayment.objects.filter(
                    is_buffer=True
                ).order_by('-updated_at').first()

            if last_updated_payment:
                last_updated_time = timezone.localtime(last_updated_payment.updated_at)
                formatted_time = last_updated_time.strftime('%d.%m.%Y %H:%M')
                return Response({
                    "last_updated": formatted_time,
                    "is_buffer": last_updated_payment.is_buffer,
                    "record_date": last_updated_payment.belge_tarih
                })
            else:
                return Response({"last_updated": "Veri bulunamadı"})

        except Exception as e:
            logger.error(f"Son güncelleme bilgisi alma hatası: {str(e)}")
            return Response({
                "error": "Son güncelleme bilgisi alınamadı",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)