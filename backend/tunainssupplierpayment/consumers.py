# backend/tunainssupplierpayment/consumers.py
import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import django
import logging

# Django uygulamalarını başlat
django.setup()

# Model importunu setup sonrasına al
from .models.models import SupplierPayment

logger = logging.getLogger(__name__)

class SupplierPaymentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'supplierpayment_group'
        
        try:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            logger.info(f"WebSocket bağlantısı başarılı: {self.channel_name}")
            await self.accept()
        except Exception as e:
            logger.error(f"WebSocket bağlantı hatası: {str(e)}")
            raise

    @database_sync_to_async
    def get_system_status(self):
        """Sistemin mevcut durumu hakkında bilgi toplar"""
        try:
            current_year = str(datetime.now().year)
            buffer_count = SupplierPayment.objects.filter(is_buffer=True).count()
            current_count = SupplierPayment.objects.filter(
                belge_tarih__startswith=current_year
            ).count()
            
            last_update = SupplierPayment.objects.filter(
                is_buffer=False
            ).order_by('-updated_at').first()
            
            status_data = {
                'current_year': current_year,
                'buffer_records': buffer_count,
                'current_year_records': current_count,
                'last_update': last_update.updated_at.strftime('%Y-%m-%d %H:%M:%S') if last_update else None,
                'total_records': buffer_count + current_count
            }
            logger.debug(f"Sistem durumu alındı: {status_data}")
            return status_data
        except Exception as e:
            logger.error(f"Durum bilgisi alma hatası: {str(e)}")
            return None

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"WebSocket bağlantısı kapatıldı: {self.channel_name}")
        except Exception as e:
            logger.error(f"WebSocket kapatma hatası: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            message = data.get('message', '')
            
            logger.debug(f"Alınan mesaj - Tür: {message_type}, İçerik: {message}")
            
            if message_type == 'status_request':
                status_info = await self.get_system_status()
                await self.send(text_data=json.dumps({
                    'type': 'status_update',
                    'data': status_info
                }))
            else:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'supplierpayment_message',
                        'message': message,
                        'message_type': message_type
                    }
                )
        except json.JSONDecodeError as e:
            logger.error(f"JSON ayrıştırma hatası: {str(e)}")
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {str(e)}")

    async def supplierpayment_message(self, event):
        try:
            message = event['message']
            message_type = event.get('message_type', 'message')
            
            if message_type == 'process_update':
                status_info = await self.get_system_status()
                response_data = {
                    'type': message_type,
                    'message': message,
                    'system_status': status_info
                }
                logger.debug(f"İşlem güncelleme yanıtı: {response_data}")
                await self.send(text_data=json.dumps(response_data))
            else:
                response_data = {
                    'type': message_type,
                    'message': message
                }
                logger.debug(f"Standart mesaj yanıtı: {response_data}")
                await self.send(text_data=json.dumps(response_data))
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {str(e)}")