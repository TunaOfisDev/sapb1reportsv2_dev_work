# backend/mailservice/api/serializers.py
from rest_framework import serializers
from ..models.models import MailLog

class MailLogSerializer(serializers.ModelSerializer):
   class Meta:
       model = MailLog
       fields = [
           'id',
           'mail_type',
           'subject', 
           'recipients',
           'status',
           'created_at',
           'sent_at',
           'has_attachments',
           'error_message',
           'related_object_type',   # Eklendi
           'related_object_id',     # Eklendi
           'created_by_email'       # Eklendi
       ]
       read_only_fields = [
           'status',
           'created_at',
           'sent_at',
           'created_by_email',
           'related_object_type',
           'related_object_id'
       ]

   def to_representation(self, instance):
       """Mail log verilerini API yanıtı için düzenle"""
       data = super().to_representation(instance)
       
       # Mail durumunu Türkçeleştir
       status_map = {
           'PENDING': 'Bekliyor',
           'SENDING': 'Gönderiliyor', 
           'SENT': 'Gönderildi',
           'FAILED': 'Başarısız'
       }
       data['status_display'] = status_map.get(data['status'], 'Bilinmiyor')
       
       # Alıcıları string olarak göster
       if data['recipients']:
           data['recipients_display'] = ', '.join(data['recipients'])
           
       return data