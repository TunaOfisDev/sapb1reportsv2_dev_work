# backend/rawmaterialwarehousestock/tasks.py

from celery import shared_task
from celery_progress.backend import ProgressRecorder
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from .models.models import RawMaterialWarehouseStock
from .utilities.data_fetcher import fetch_hana_db_data
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def fetch_and_update_hana_data(self, token):
    progress_recorder = ProgressRecorder(self)
    channel_layer = get_channel_layer()
    try:
        logger.info("Fetching data from HANA DB")
        hana_data = fetch_hana_db_data(token)
        
        if not hana_data:
            logger.warning("No data fetched from HANA DB")
            async_to_sync(channel_layer.group_send)(
                'rawmaterialwarehousestock_group',
                {
                    'type': 'rawmaterialwarehousestock_message',
                    'message': 'Failed to fetch data from HANA DB or no new data found.'
                }
            )
            return
        
        total_data = len(hana_data)
        logger.info(f"Fetched {total_data} items from HANA DB")

        # Kalem kodlarının benzersizliğini kontrol et
        kalem_kod_count = defaultdict(int)
        for item in hana_data:
            kalem_kod_count[item['KalemKod']] += 1
        
        duplicate_kalem_kods = [k for k, v in kalem_kod_count.items() if v > 1]
        if duplicate_kalem_kods:
            logger.warning(f"Duplicate kalem_kod found in HANA data: {duplicate_kalem_kods}")
            async_to_sync(channel_layer.group_send)(
                'rawmaterialwarehousestock_group',
                {
                    'type': 'rawmaterialwarehousestock_message',
                    'message': f'Duplicate kalem_kod found in HANA data: {duplicate_kalem_kods}'
                }
            )

        # HANA'dan gelen tüm kalem kodlarını topla
        hana_item_codes = set(item['KalemKod'] for item in hana_data)

        # HANA veritabanındaki her bir kalem kod için veritabanını güncelle veya oluştur
        for i, item in enumerate(hana_data):
            try:
                stock, created = RawMaterialWarehouseStock.objects.update_or_create(
                    kalem_kod=item['KalemKod'],
                    defaults={
                        'depo_kodu': item['DepoKod'],
                        'kalem_grup_ad': item['KalemGrupAd'],
                        'stok_kalem': item['StokKalem'] == 'Y',
                        'satis_kalem': item['SatisKalem'] == 'Y',
                        'satinalma_kalem': item['SatinalmaKalem'] == 'Y',
                        'yapay_kalem': item['YapayKalem'] == 'Y',
                        'kalem_tanim': item.get('Kalemtanim') or 'Bilinmeyen',
                        'stok_olcu_birim': item.get('StokOlcuBirim') or 'None',
                        'depo_stok': item['DepoStok'],
                        'siparis_edilen_miktar': item['AcikSiparisEdilenMiktar'],
                        'son_satinalma_fiyat': item['SonSatınalmaFiyat'],
                        'son_satinalma_fatura_tarih': datetime.strptime(item['SonSatinalmaFaturaTarih'], '%d.%m.%Y').date(),
                        'verilen_siparisler': item['VerilenSiparisler'],
                        'secili': False,
                        'hide_zero_stock': False,
                    }
                )
                logger.info(f"Processed item {i + 1}/{total_data}: {item['KalemKod']}")
                progress_recorder.set_progress(i + 1, total_data, description=f"Processing {i + 1} of {total_data}")
            except Exception as e:
                logger.error(f"Error processing item {item['KalemKod']}: {str(e)}")
                async_to_sync(channel_layer.group_send)(
                    'rawmaterialwarehousestock_group',
                    {
                        'type': 'rawmaterialwarehousestock_message',
                        'message': f'Error processing item {item["KalemKod"]}: {str(e)}'
                    }
                )

        # HANA'da olmayan kalem kodlarını API veritabanından sil
        deleted_count = RawMaterialWarehouseStock.objects.exclude(kalem_kod__in=hana_item_codes).delete()[0]
        logger.info(f"Deleted {deleted_count} items that were not in HANA data")

        logger.info("Successfully fetched and updated raw material warehouse stock data.")
        async_to_sync(channel_layer.group_send)(
            'rawmaterialwarehousestock_group',
            {
                'type': 'rawmaterialwarehousestock_message',
                'message': 'Raw material warehouse stock data successfully fetched and updated.'
            }
        )
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        async_to_sync(channel_layer.group_send)(
            'rawmaterialwarehousestock_group',
            {
                'type': 'rawmaterialwarehousestock_message',
                'message': f'An error occurred: {str(e)}'
            }
        )