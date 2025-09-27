# backend/supplierpayment/tasks.py
from datetime import datetime, timedelta
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.db.models import Max
from .models.models import SupplierPayment
from .utilities.data_fetcher import fetch_hana_db_data
from .api.closinginvoice_view import SupplierPaymentSimulation
from loguru import logger

logger.add("logs/backend.log", rotation="1 MB")

def get_cutoff_date():
    """Son 120 günün başlangıç tarihini hesaplar"""
    today = datetime.now().date()
    cutoff_date = today - timedelta(days=120)
    return cutoff_date.strftime("%Y-%m-%d")

@shared_task(bind=True)
def fetch_and_update_supplier_payments(self, token):
    import time
    start_time = time.time()
    
    progress_recorder = ProgressRecorder(self)
    channel_layer = get_channel_layer()
    
    try:
        # 1. HANA DB'den verileri al
        hana_data = fetch_hana_db_data(token)
        
        if not hana_data:
            async_to_sync(channel_layer.group_send)(
                'supplierpayment_group',
                {
                    'type': 'supplierpayment_message',
                    'message': 'HANA DB\'den veri çekilemedi veya yeni veri bulunamadı.',
                    'message_type': 'error'
                }
            )
            return {
                'status': 'error',
                'message': 'HANA DB\'den veri çekilemedi veya yeni veri bulunamadı.'
            }
        
        total_data = len(hana_data)
        
        # 2. İlerleme bilgisi gönder
        async_to_sync(channel_layer.group_send)(
            'supplierpayment_group',
            {
                'type': 'supplierpayment_message',
                'message': f'Toplam {total_data} kayıt işlenmeye başlanıyor...',
                'message_type': 'info'
            }
        )
        
        # 3. HANA verilerinden dictionary oluştur
        hana_records = {}
        for data in hana_data:
            key = f"{data['BELGE_NO']}_{data['CARI_KOD']}_{data['BELGE_TARIH']}"
            hana_records[key] = data
        
        with transaction.atomic():
            # 4. Yerel veritabanından sadece gerekli alanları çek (bellek kullanımını azaltır)
            local_keys = {
                f"{record[0]}_{record[1]}_{record[2]}": record[3]
                for record in SupplierPayment.objects.values_list('belge_no', 'cari_kod', 'belge_tarih', 'id')
            }
            
            # 5. Silinecek kayıtları belirle
            to_delete_ids = [
                record_id for key, record_id in local_keys.items()
                if key not in hana_records
            ]
            
            # 6. Silinecek kayıtları toplu olarak sil
            deleted_count = 0
            if to_delete_ids:
                deleted_count = SupplierPayment.objects.filter(id__in=to_delete_ids).delete()[0]
                logger.info(f"{deleted_count} kayıt HANA DB'de bulunamadığı için silindi.")
            
            # 7. Eklenecek ve güncellenecek kayıtları hazırla
            current_year = str(datetime.now().year)
            to_create = []
            to_update = []
            buffer_count = 0
            
            for i, (key, data) in enumerate(hana_records.items()):
                belge_tarih = data['BELGE_TARIH']
                year = belge_tarih.split('-')[0]
                is_buffer = year != current_year
                
                if is_buffer:
                    buffer_count += 1
                
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
                
                if key in local_keys:
                    # Güncelleme
                    record_data['id'] = local_keys[key]
                    to_update.append(record_data)
                else:
                    # Yeni kayıt
                    to_create.append(SupplierPayment(**record_data))
                
                # İlerleme bilgisi
                if (i + 1) % 1000 == 0 or i == len(hana_records) - 1:
                    progress_recorder.set_progress(
                        i + 1,
                        len(hana_records),
                        description=f"{i + 1}/{len(hana_records)} kayıt işlendi"
                    )
                    
                    async_to_sync(channel_layer.group_send)(
                        'supplierpayment_group',
                        {
                            'type': 'supplierpayment_message',
                            'message': f"{i + 1}/{len(hana_records)} kayıt işlendi",
                            'message_type': 'process_update'
                        }
                    )
            
            # 8. Yeni kayıtları toplu olarak ekle
            created_count = 0
            if to_create:
                created_count = len(to_create)
                SupplierPayment.objects.bulk_create(to_create, batch_size=1000)
                logger.info(f"{created_count} yeni kayıt eklendi.")
            
            # 9. Güncellenecek kayıtları toplu olarak güncelle
            updated_count = 0
            if to_update:
                # Django bulk_update için hazırla
                update_objects = []
                for data in to_update:
                    obj_id = data.pop('id')
                    obj = SupplierPayment(id=obj_id, **data)
                    update_objects.append(obj)
                
                if update_objects:
                    updated_count = len(update_objects)
                    fields_to_update = ['cari_ad', 'iban', 'odemekosulu', 'borc', 'alacak', 'is_buffer']
                    SupplierPayment.objects.bulk_update(update_objects, fields_to_update, batch_size=1000)
                    logger.info(f"{updated_count} kayıt güncellendi.")
            
            # 10. Kapanış faturalarını güncelle
            logger.info("Kapanış faturaları güncelleniyor...")
            simulation = SupplierPaymentSimulation()
            simulation.process_transactions()
            simulation.generate_payment_list()
            logger.info("Kapanış faturaları güncellendi.")
        
        # İşlem süresini hesapla
        elapsed_time = time.time() - start_time
        
        # 11. Özet bilgiyi gönder
        summary_message = (
            f'Veri güncelleme tamamlandı ({round(elapsed_time, 2)} saniye). '
            f'Yeni eklenen: {created_count}, Güncellenen: {updated_count}, '
            f'Silinen: {deleted_count}, Buffer kayıtları: {buffer_count}'
        )
        
        async_to_sync(channel_layer.group_send)(
            'supplierpayment_group',
            {
                'type': 'supplierpayment_message',
                'message': summary_message,
                'message_type': 'success'
            }
        )
        
        return {
            'status': 'success',
            'message': summary_message,
            'new_records': created_count,
            'updated_records': updated_count,
            'deleted_records': deleted_count,
            'buffer_records': buffer_count,
            'process_time_seconds': round(elapsed_time, 2)
        }
    
    except Exception as e:
        error_message = f'Veri güncelleme sırasında hata oluştu: {str(e)}'
        logger.error(error_message)
        
        async_to_sync(channel_layer.group_send)(
            'supplierpayment_group',
            {
                'type': 'supplierpayment_message',
                'message': error_message,
                'message_type': 'error'
            }
        )
        
        return {
            'status': 'error',
            'message': error_message
        }