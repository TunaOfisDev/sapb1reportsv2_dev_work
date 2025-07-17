# backend/sapbot_api/tasks/notification_tasks.py
"""
SAPBot API Notification Tasks

Bu modül bildirim görevlerini içerir:
- Email bildirimleri
- Sistem uyarıları
- Kullanıcı bildirimleri
- Webhook bildirimleri
- Slack/Teams entegrasyonu
- Push notification
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db import models
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from celery import shared_task
from celery.utils.log import get_task_logger

from ..models import (
   SystemNotification, ErrorLog, 
   QueryAnalytics, DocumentSource, ChatConversation
)
from ..utils.helpers import format_file_size, time_ago, format_currency

User = get_user_model()
logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_email_notification(
   self,
   recipient_email: str,
   subject: str,
   message: str,
   template_name: Optional[str] = None,
   context: Optional[Dict] = None,
   attachments: Optional[List[str]] = None,
   is_html: bool = True
):
   """Email bildirimi gönder"""
   try:
       logger.info(f"📧 Email gönderiliyor: {recipient_email}")
       
       # Template kullanımı
       if template_name and context:
           try:
               html_content = render_to_string(f'emails/{template_name}.html', context)
               text_content = render_to_string(f'emails/{template_name}.txt', context)
               
               email = EmailMultiAlternatives(
                   subject=subject,
                   body=text_content,
                   from_email=settings.DEFAULT_FROM_EMAIL,
                   to=[recipient_email]
               )
               email.attach_alternative(html_content, "text/html")
               
               # Ekleri ekle
               if attachments:
                   for attachment_path in attachments:
                       if os.path.exists(attachment_path):
                           email.attach_file(attachment_path)
               
               email.send()
               
           except Exception as template_error:
               logger.warning(f"⚠️ Template hatası, basit email gönderiliyor: {template_error}")
               # Template başarısızsa basit email gönder
               send_mail(
                   subject=subject,
                   message=message,
                   from_email=settings.DEFAULT_FROM_EMAIL,
                   recipient_list=[recipient_email],
                   html_message=message if is_html else None
               )
       else:
           # Basit email
           send_mail(
               subject=subject,
               message=message,
               from_email=settings.DEFAULT_FROM_EMAIL,
               recipient_list=[recipient_email],
               html_message=message if is_html else None
           )
       
       logger.info(f"✅ Email başarıyla gönderildi: {recipient_email}")
       
       return {
           'success': True,
           'recipient': recipient_email,
           'subject': subject,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Email gönderme hatası ({recipient_email}): {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def send_bulk_email_notifications(self, email_list: List[Dict[str, Any]]):
   """Toplu email bildirimi"""
   try:
       logger.info(f"📧 Toplu email gönderimi başlıyor: {len(email_list)} alıcı")
       
       results = {
           'total_emails': len(email_list),
           'sent_successfully': 0,
           'failed': 0,
           'errors': [],
           'timestamp': timezone.now().isoformat()
       }
       
       for email_data in email_list:
           try:
               send_email_notification.delay(
                   recipient_email=email_data['email'],
                   subject=email_data['subject'],
                   message=email_data['message'],
                   template_name=email_data.get('template'),
                   context=email_data.get('context'),
                   is_html=email_data.get('is_html', True)
               )
               results['sent_successfully'] += 1
               
           except Exception as e:
               results['failed'] += 1
               results['errors'].append({
                   'email': email_data['email'],
                   'error': str(e)
               })
               logger.error(f"❌ Toplu email hatası ({email_data['email']}): {e}")
       
       logger.info(f"✅ Toplu email tamamlandı: {results['sent_successfully']}/{results['total_emails']}")
       
       return results
       
   except Exception as exc:
       logger.error(f"❌ Toplu email hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_slack_notification(
   self,
   message: str,
   channel: str = '#sapbot-alerts',
   username: str = 'SAPBot',
   icon_emoji: str = ':robot_face:',
   color: str = 'good',
   attachment_fields: Optional[List[Dict]] = None
):
   """Slack bildirimi gönder"""
   try:
       slack_webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
       
       if not slack_webhook_url:
           logger.warning("⚠️ Slack webhook URL tanımlı değil")
           return {'success': False, 'error': 'webhook_not_configured'}
       
       logger.info(f"📢 Slack bildirimi gönderiliyor: {channel}")
       
       # Slack payload hazırla
       payload = {
           'channel': channel,
           'username': username,
           'icon_emoji': icon_emoji,
           'text': message
       }
       
       # Attachment (detaylı mesaj) ekle
       if attachment_fields:
           payload['attachments'] = [{
               'color': color,
               'fields': attachment_fields,
               'footer': 'SAPBot API',
               'ts': int(timezone.now().timestamp())
           }]
       
       # Slack'e gönder
       response = requests.post(
           slack_webhook_url,
           json=payload,
           timeout=10
       )
       
       if response.status_code == 200:
           logger.info("✅ Slack bildirimi başarıyla gönderildi")
           return {
               'success': True,
               'channel': channel,
               'timestamp': timezone.now().isoformat()
           }
       else:
           logger.error(f"❌ Slack API hatası: {response.status_code} - {response.text}")
           raise Exception(f"Slack API error: {response.status_code}")
       
   except Exception as exc:
       logger.error(f"❌ Slack bildirim hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_teams_notification(
   self,
   title: str,
   message: str,
   color: str = '0078D4',
   facts: Optional[List[Dict]] = None
):
   """Microsoft Teams bildirimi gönder"""
   try:
       teams_webhook_url = getattr(settings, 'TEAMS_WEBHOOK_URL', None)
       
       if not teams_webhook_url:
           logger.warning("⚠️ Teams webhook URL tanımlı değil")
           return {'success': False, 'error': 'webhook_not_configured'}
       
       logger.info("📢 Teams bildirimi gönderiliyor")
       
       # Teams payload hazırla
       payload = {
           "@type": "MessageCard",
           "@context": "http://schema.org/extensions",
           "themeColor": color,
           "summary": title,
           "sections": [{
               "activityTitle": title,
               "activitySubtitle": f"SAPBot API - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
               "text": message,
               "markdown": True
           }]
       }
       
       # Fact'ları ekle (key-value çiftleri)
       if facts:
           payload["sections"][0]["facts"] = facts
       
       # Teams'e gönder
       response = requests.post(
           teams_webhook_url,
           json=payload,
           timeout=10
       )
       
       if response.status_code == 200:
           logger.info("✅ Teams bildirimi başarıyla gönderildi")
           return {
               'success': True,
               'title': title,
               'timestamp': timezone.now().isoformat()
           }
       else:
           logger.error(f"❌ Teams API hatası: {response.status_code} - {response.text}")
           raise Exception(f"Teams API error: {response.status_code}")
       
   except Exception as exc:
       logger.error(f"❌ Teams bildirim hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def send_webhook_notification(
   self,
   webhook_url: str,
   payload: Dict[str, Any],
   headers: Optional[Dict[str, str]] = None,
   method: str = 'POST'
):
   """Generic webhook bildirimi"""
   try:
       logger.info(f"🔗 Webhook bildirimi: {webhook_url}")
       
       # Default headers
       default_headers = {
           'Content-Type': 'application/json',
           'User-Agent': 'SAPBot-API/1.0'
       }
       
       if headers:
           default_headers.update(headers)
       
       # Timestamp ekle
       payload['timestamp'] = timezone.now().isoformat()
       payload['source'] = 'sapbot-api'
       
       # HTTP isteği gönder
       response = requests.request(
           method=method,
           url=webhook_url,
           json=payload,
           headers=default_headers,
           timeout=30
       )
       
       if 200 <= response.status_code < 300:
           logger.info(f"✅ Webhook başarıyla gönderildi: {response.status_code}")
           return {
               'success': True,
               'status_code': response.status_code,
               'response': response.text[:500],  # İlk 500 karakter
               'timestamp': timezone.now().isoformat()
           }
       else:
           logger.error(f"❌ Webhook hatası: {response.status_code} - {response.text}")
           raise Exception(f"Webhook error: {response.status_code}")
       
   except Exception as exc:
       logger.error(f"❌ Webhook gönderim hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def notify_system_alert(
   self,
   alert_type: str,
   severity: str,
   message: str,
   details: Optional[Dict] = None,
   notify_channels: Optional[List[str]] = None
):
   """Sistem uyarısı gönder"""
   try:
       logger.info(f"🚨 Sistem uyarısı: {alert_type} - {severity}")
       
       # Varsayılan bildirim kanalları
       if not notify_channels:
           notify_channels = ['email', 'slack']
       
       # Uyarı renklerini belirle
       color_map = {
           'info': 'good',
           'warning': 'warning', 
           'error': 'danger',
           'critical': 'danger'
       }
       
       teams_color_map = {
           'info': '0078D4',
           'warning': 'FFA500',
           'error': 'FF0000',
           'critical': 'FF0000'
       }
       
       notification_results = []
       
       # Email bildirimi
       if 'email' in notify_channels:
           try:
               # Admin kullanıcıları al
               admin_users = User.objects.filter(
                   is_superuser=True,
                   is_active=True
               ).exclude(email='')
               
               for admin in admin_users:
                   # Email template context
                   email_context = {
                       'alert_type': alert_type,
                       'severity': severity.upper(),
                       'message': message,
                       'details': details or {},
                       'timestamp': timezone.now(),
                       'user_name': admin.first_name or admin.username
                   }
                   
                   send_email_notification.delay(
                       recipient_email=admin.email,
                       subject=f"🚨 SAPBot Sistem Uyarısı - {severity.upper()}",
                       message=message,
                       template_name='system_alert',
                       context=email_context
                   )
               
               notification_results.append({'channel': 'email', 'status': 'sent'})
               
           except Exception as e:
               logger.error(f"❌ Email uyarı hatası: {e}")
               notification_results.append({'channel': 'email', 'status': 'failed', 'error': str(e)})
       
       # Slack bildirimi
       if 'slack' in notify_channels:
           try:
               # Slack attachment fields
               slack_fields = [
                   {'title': 'Uyarı Tipi', 'value': alert_type, 'short': True},
                   {'title': 'Önem Derecesi', 'value': severity.upper(), 'short': True},
                   {'title': 'Zaman', 'value': timezone.now().strftime('%Y-%m-%d %H:%M:%S'), 'short': True}
               ]
               
               if details:
                   for key, value in details.items():
                       slack_fields.append({
                           'title': key.replace('_', ' ').title(),
                           'value': str(value),
                           'short': True
                       })
               
               send_slack_notification.delay(
                   message=f"🚨 *Sistem Uyarısı*\n{message}",
                   color=color_map.get(severity, 'warning'),
                   attachment_fields=slack_fields
               )
               
               notification_results.append({'channel': 'slack', 'status': 'sent'})
               
           except Exception as e:
               logger.error(f"❌ Slack uyarı hatası: {e}")
               notification_results.append({'channel': 'slack', 'status': 'failed', 'error': str(e)})
       
       # Teams bildirimi
       if 'teams' in notify_channels:
           try:
               teams_facts = []
               teams_facts.append({'name': 'Uyarı Tipi', 'value': alert_type})
               teams_facts.append({'name': 'Önem Derecesi', 'value': severity.upper()})
               
               if details:
                   for key, value in details.items():
                       teams_facts.append({
                           'name': key.replace('_', ' ').title(),
                           'value': str(value)
                       })
               
               send_teams_notification.delay(
                   title=f"🚨 SAPBot Sistem Uyarısı - {severity.upper()}",
                   message=message,
                   color=teams_color_map.get(severity, 'FFA500'),
                   facts=teams_facts
               )
               
               notification_results.append({'channel': 'teams', 'status': 'sent'})
               
           except Exception as e:
               logger.error(f"❌ Teams uyarı hatası: {e}")
               notification_results.append({'channel': 'teams', 'status': 'failed', 'error': str(e)})
       
       # Sistem bildirimi kaydet
       SystemNotification.objects.create(
           title=f"Sistem Uyarısı - {alert_type}",
           message=message,
           notification_type=severity,
           priority=4 if severity == 'critical' else 3 if severity == 'error' else 2,
           is_system_wide=True,
           expires_at=timezone.now() + timedelta(hours=24)
       )
       
       logger.info(f"✅ Sistem uyarısı gönderildi: {len(notification_results)} kanal")
       
       return {
           'success': True,
           'alert_type': alert_type,
           'severity': severity,
           'channels_notified': notification_results,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Sistem uyarı hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def notify_document_processing_completed(self, document_id: str):
   """Döküman işleme tamamlandı bildirimi"""
   try:
       document = DocumentSource.objects.get(id=document_id)
       logger.info(f"📄 Döküman işleme bildirimi: {document.title}")
       
       # Yükleyen kullanıcıya bildir
       if document.uploaded_by and document.uploaded_by.email:
           email_context = {
               'document_title': document.title,
               'document_type': document.get_document_type_display(),
               'chunk_count': document.chunk_count,
               'processing_time': time_ago(document.processed_at) if document.processed_at else 'Bilinmiyor',
               'user_name': document.uploaded_by.first_name or document.uploaded_by.username
           }
           
           send_email_notification.delay(
               recipient_email=document.uploaded_by.email,
               subject=f"✅ Döküman İşleme Tamamlandı - {document.title}",
               message=f"Merhaba {email_context['user_name']},\n\nYüklediğiniz '{document.title}' dökümanı başarıyla işlendi.",
               template_name='document_processed',
               context=email_context
           )
       
       # Slack bildirimi (opsiyonel)
       if getattr(settings, 'SLACK_WEBHOOK_URL', None):
           slack_fields = [
               {'title': 'Döküman', 'value': document.title, 'short': False},
               {'title': 'Tip', 'value': document.get_document_type_display(), 'short': True},
               {'title': 'Chunk Sayısı', 'value': str(document.chunk_count), 'short': True},
               {'title': 'Yükleyen', 'value': document.uploaded_by.email if document.uploaded_by else 'Sistem', 'short': True}
           ]
           
           send_slack_notification.delay(
               message=f"📄 Döküman işleme tamamlandı: *{document.title}*",
               channel='#sapbot-documents',
               color='good',
               attachment_fields=slack_fields
           )
       
       return {
           'success': True,
           'document_id': document_id,
           'document_title': document.title,
           'notification_sent': True,
           'timestamp': timezone.now().isoformat()
       }
       
   except DocumentSource.DoesNotExist:
       logger.error(f"❌ Döküman bulunamadı: {document_id}")
       return {'success': False, 'error': 'document_not_found'}
   except Exception as exc:
       logger.error(f"❌ Döküman bildirim hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def notify_system_maintenance(
   self,
   maintenance_type: str,
   start_time: str,
   duration_minutes: int,
   affected_services: List[str],
   description: str
):
   """Sistem bakım bildirimi"""
   try:
       logger.info(f"🔧 Bakım bildirimi: {maintenance_type}")
       
       # Bakım zamanını parse et
       start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
       end_dt = start_dt + timedelta(minutes=duration_minutes)
       
       # Tüm aktif kullanıcılara email gönder
       active_users = User.objects.filter(
           is_active=True,
           sapbot_profile__email_notifications=True
       ).exclude(email='')
       
       email_list = []
       for user in active_users:
           email_context = {
               'user_name': user.first_name or user.username,
               'maintenance_type': maintenance_type,
               'start_time': start_dt.strftime('%d.%m.%Y %H:%M'),
               'end_time': end_dt.strftime('%d.%m.%Y %H:%M'),
               'duration': f"{duration_minutes} dakika",
               'affected_services': affected_services,
               'description': description
           }
           
           email_list.append({
               'email': user.email,
               'subject': f"🔧 SAPBot Sistem Bakımı - {maintenance_type}",
               'message': f"Merhaba {email_context['user_name']},\n\nSistem bakımı planlanmıştır.",
               'template': 'maintenance_notification',
               'context': email_context
           })
       
       # Toplu email gönder
       if email_list:
           send_bulk_email_notifications.delay(email_list)
       
       # Slack bildirimi
       if getattr(settings, 'SLACK_WEBHOOK_URL', None):
           slack_fields = [
               {'title': 'Bakım Tipi', 'value': maintenance_type, 'short': True},
               {'title': 'Başlangıç', 'value': start_dt.strftime('%d.%m.%Y %H:%M'), 'short': True},
               {'title': 'Süre', 'value': f"{duration_minutes} dakika", 'short': True},
               {'title': 'Etkilenen Servisler', 'value': ', '.join(affected_services), 'short': False}
           ]
           
           send_slack_notification.delay(
               message=f"🔧 *Sistem Bakımı Planlandı*\n{description}",
               color='warning',
               attachment_fields=slack_fields
           )
       
       # Sistem bildirimi oluştur
       SystemNotification.objects.create(
           title=f"Sistem Bakımı - {maintenance_type}",
           message=f"{description}\n\nBaşlangıç: {start_dt.strftime('%d.%m.%Y %H:%M')}\nSüre: {duration_minutes} dakika",
           notification_type='warning',
           priority=3,
           is_system_wide=True,
           expires_at=end_dt + timedelta(hours=1)
       )
       
       return {
           'success': True,
           'maintenance_type': maintenance_type,
           'users_notified': len(email_list),
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Bakım bildirim hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def send_daily_summary_report(self):
   """Günlük özet raporu gönder"""
   try:
       logger.info("📊 Günlük özet raporu hazırlanıyor...")
       
       today = timezone.now().date()
       yesterday = today - timedelta(days=1)
       
       # Günlük istatistikler
       daily_stats = {
           'date': yesterday.strftime('%d.%m.%Y'),
           'total_queries': QueryAnalytics.objects.filter(
               created_at__date=yesterday
           ).count(),
           'unique_users': QueryAnalytics.objects.filter(
               created_at__date=yesterday
           ).values('user').distinct().count(),
           'successful_queries': QueryAnalytics.objects.filter(
               created_at__date=yesterday,
               response_generated=True
           ).count(),
           'documents_processed': DocumentSource.objects.filter(
               processed_at__date=yesterday
           ).count(),
           'new_conversations': ChatConversation.objects.filter(
               created_at__date=yesterday
           ).count(),
           'system_errors': ErrorLog.objects.filter(
               created_at__date=yesterday,
               error_level__in=['ERROR', 'CRITICAL']
           ).count()
       }
       
       # Başarı oranı hesapla
       if daily_stats['total_queries'] > 0:
           daily_stats['success_rate'] = round(
               (daily_stats['successful_queries'] / daily_stats['total_queries']) * 100, 1
           )
       else:
           daily_stats['success_rate'] = 0
       
       # En çok kullanılan SAP modülleri
       top_sap_modules = QueryAnalytics.objects.filter(
           created_at__date=yesterday,
           sap_module_detected__isnull=False
       ).values_list('sap_module_detected', flat=True)
       
       from collections import Counter
       module_counter = Counter(top_sap_modules)
       daily_stats['top_sap_modules'] = dict(module_counter.most_common(5))
       
       # Performans metrikleri
       avg_response_time = QueryAnalytics.objects.filter(
           created_at__date=yesterday,
           response_time__isnull=False
       ).aggregate(avg_time=models.Avg('response_time'))['avg_time']
       
       daily_stats['avg_response_time'] = round(avg_response_time, 2) if avg_response_time else 0
       
       # Admin kullanıcılara rapor gönder
       admin_users = User.objects.filter(
           is_superuser=True,
           is_active=True
       ).exclude(email='')
       
       email_list = []
       for admin in admin_users:
           email_context = {
               'admin_name': admin.first_name or admin.username,
               'stats': daily_stats,
               'report_date': yesterday.strftime('%d %B %Y')
           }
           
           email_list.append({
               'email': admin.email,
               'subject': f"📊 SAPBot Günlük Rapor - {daily_stats['date']}",
               'message': f"Merhaba {email_context['admin_name']},\n\n{daily_stats['date']} tarihli günlük rapor hazır.",
               'template': 'daily_summary',
               'context': email_context
           })
       
       # Toplu email gönder
       if email_list:
           send_bulk_email_notifications.delay(email_list)
       
       # Slack özet bildirimi
       if getattr(settings, 'SLACK_WEBHOOK_URL', None):
           slack_fields = [
               {'title': 'Toplam Sorgu', 'value': str(daily_stats['total_queries']), 'short': True},
               {'title': 'Benzersiz Kullanıcı', 'value': str(daily_stats['unique_users']), 'short': True},
               {'title': 'Başarı Oranı', 'value': f"%{daily_stats['success_rate']}", 'short': True},
               {'title': 'Ortalama Yanıt Süresi', 'value': f"{daily_stats['avg_response_time']}s", 'short': True},
               {'title': 'İşlenen Döküman', 'value': str(daily_stats['documents_processed']), 'short': True},
               {'title': 'Sistem Hataları', 'value': str(daily_stats['system_errors']), 'short': True}
           ]
           
           send_slack_notification.delay(
               message=f"📊 *Günlük Özet Raporu - {daily_stats['date']}*",
               channel='#sapbot-reports',
               color='good',
               attachment_fields=slack_fields
           )
       
       logger.info(f"✅ Günlük özet raporu gönderildi: {len(email_list)} admin")
       
       return {
           'success': True,
           'report_date': daily_stats['date'],
           'admins_notified': len(email_list),
           'stats': daily_stats,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Günlük rapor hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def send_weekly_analytics_report(self):
   """Haftalık analitik raporu gönder"""
   try:
       logger.info("📈 Haftalık analitik raporu hazırlanıyor...")
       
       # Son hafta
       end_date = timezone.now().date()
       start_date = end_date - timedelta(days=7)
       
       # Haftalık istatistikler
       weekly_stats = {
           'week_start': start_date.strftime('%d.%m.%Y'),
           'week_end': end_date.strftime('%d.%m.%Y'),
           'total_queries': QueryAnalytics.objects.filter(
               created_at__date__gte=start_date,
               created_at__date__lt=end_date
           ).count(),
           'unique_users': QueryAnalytics.objects.filter(
               created_at__date__gte=start_date,
               created_at__date__lt=end_date
           ).values('user').distinct().count(),
           'total_conversations': ChatConversation.objects.filter(
               created_at__date__gte=start_date,
               created_at__date__lt=end_date
           ).count(),
           'documents_uploaded': DocumentSource.objects.filter(
               created_at__date__gte=start_date,
               created_at__date__lt=end_date
           ).count(),
           'chunks_created': 0  # Bu ayrı hesaplanacak
       }
       
       # Chunk sayısı hesapla
       from ..models import KnowledgeChunk
       weekly_stats['chunks_created'] = KnowledgeChunk.objects.filter(
           created_at__date__gte=start_date,
           created_at__date__lt=end_date
       ).count()
       
       # Günlük dağılım
       daily_breakdown = []
       for i in range(7):
           date = start_date + timedelta(days=i)
           daily_queries = QueryAnalytics.objects.filter(
               created_at__date=date
           ).count()
           daily_breakdown.append({
               'date': date.strftime('%d.%m'),
               'queries': daily_queries
           })
       
       weekly_stats['daily_breakdown'] = daily_breakdown
       
       # SAP modül analizi
       sap_module_stats = {}
       for module_code, module_name in [
           ('FI', 'Mali Muhasebe'),
           ('MM', 'Malzeme Yönetimi'),
           ('SD', 'Satış ve Dağıtım'),
           ('CRM', 'Müşteri İlişkileri'),
           ('HR', 'İnsan Kaynakları')
       ]:
           count = QueryAnalytics.objects.filter(
               created_at__date__gte=start_date,
               created_at__date__lt=end_date,
               sap_module_detected=module_code
           ).count()
           if count > 0:
               sap_module_stats[module_name] = count
       
       weekly_stats['sap_module_usage'] = sap_module_stats
       
       # Intent analizi
       intent_stats = {}
       for intent_code, intent_name in [
           ('how_to', 'Nasıl Yapılır'),
           ('error_solving', 'Hata Çözme'),
           ('explanation', 'Açıklama'),
           ('configuration', 'Konfigürasyon')
       ]:
           count = QueryAnalytics.objects.filter(
               created_at__date__gte=start_date,
               created_at__date__lt=end_date,
               intent_detected=intent_code
           ).count()
           if count > 0:
               intent_stats[intent_name] = count
       
       weekly_stats['intent_distribution'] = intent_stats
       
       # Performans metrikleri
       performance_data = QueryAnalytics.objects.filter(
           created_at__date__gte=start_date,
           created_at__date__lt=end_date,
           response_time__isnull=False
       ).aggregate(
           avg_response_time=models.Avg('response_time'),
           min_response_time=models.Min('response_time'),
           max_response_time=models.Max('response_time')
       )
       
       weekly_stats['performance'] = {
           'avg_response_time': round(performance_data['avg_response_time'] or 0, 2),
           'min_response_time': round(performance_data['min_response_time'] or 0, 2),
           'max_response_time': round(performance_data['max_response_time'] or 0, 2)
       }
       
       # Hata analizi
       error_breakdown = ErrorLog.objects.filter(
           created_at__date__gte=start_date,
           created_at__date__lt=end_date
       ).values('error_level').annotate(
           count=models.Count('id')
       )
       
       weekly_stats['error_breakdown'] = {
           item['error_level']: item['count'] 
           for item in error_breakdown
       }
       
       # En aktif kullanıcılar (anonimleştirilmiş)
       top_users = QueryAnalytics.objects.filter(
           created_at__date__gte=start_date,
           created_at__date__lt=end_date,
           user__isnull=False
       ).values('user__email').annotate(
           query_count=models.Count('id')
       ).order_by('-query_count')[:5]
       
       weekly_stats['top_users'] = [
           {
               'user': f"Kullanıcı{i+1}",  # Anonimleştir
               'query_count': user['query_count']
           }
           for i, user in enumerate(top_users)
       ]
       
       # Büyüme analizi (önceki haftayla karşılaştırma)
       prev_week_start = start_date - timedelta(days=7)
       prev_week_queries = QueryAnalytics.objects.filter(
           created_at__date__gte=prev_week_start,
           created_at__date__lt=start_date
       ).count()
       
       if prev_week_queries > 0:
           growth_rate = ((weekly_stats['total_queries'] - prev_week_queries) / prev_week_queries) * 100
           weekly_stats['growth_rate'] = round(growth_rate, 1)
       else:
           weekly_stats['growth_rate'] = 0
       
       # Admin kullanıcılara gönder
       admin_users = User.objects.filter(
           is_superuser=True,
           is_active=True
       ).exclude(email='')
       
       email_list = []
       for admin in admin_users:
           email_context = {
               'admin_name': admin.first_name or admin.username,
               'stats': weekly_stats,
               'week_period': f"{weekly_stats['week_start']} - {weekly_stats['week_end']}"
           }
           
           email_list.append({
               'email': admin.email,
               'subject': f"📈 SAPBot Haftalık Analitik Raporu - {weekly_stats['week_start']}",
               'message': f"Merhaba {email_context['admin_name']},\n\nHaftalık analitik raporu hazır.",
               'template': 'weekly_analytics',
               'context': email_context
           })
       
       # Toplu email gönder
       if email_list:
           send_bulk_email_notifications.delay(email_list)
       
       # Slack detaylı rapor
       if getattr(settings, 'SLACK_WEBHOOK_URL', None):
           slack_fields = [
               {'title': 'Toplam Sorgu', 'value': f"{weekly_stats['total_queries']} (Büyüme: %{weekly_stats['growth_rate']})", 'short': True},
               {'title': 'Benzersiz Kullanıcı', 'value': str(weekly_stats['unique_users']), 'short': True},
               {'title': 'Yeni Konuşma', 'value': str(weekly_stats['total_conversations']), 'short': True},
               {'title': 'Döküman Yüklendi', 'value': str(weekly_stats['documents_uploaded']), 'short': True},
               {'title': 'Chunk Oluşturuldu', 'value': str(weekly_stats['chunks_created']), 'short': True},
               {'title': 'Ortalama Yanıt Süresi', 'value': f"{weekly_stats['performance']['avg_response_time']}s", 'short': True}
           ]
           
           # En çok kullanılan modül
           if weekly_stats['sap_module_usage']:
               top_module = max(weekly_stats['sap_module_usage'], key=weekly_stats['sap_module_usage'].get)
               slack_fields.append({
                   'title': 'En Çok Kullanılan Modül',
                   'value': f"{top_module} ({weekly_stats['sap_module_usage'][top_module]})",
                   'short': True
               })
           
           send_slack_notification.delay(
               message=f"📈 *Haftalık Analitik Raporu*\n{weekly_stats['week_start']} - {weekly_stats['week_end']}",
               channel='#sapbot-analytics',
               color='good',
               attachment_fields=slack_fields
           )
       
       logger.info(f"✅ Haftalık analitik raporu gönderildi: {len(email_list)} admin")
       
       return {
           'success': True,
           'week_period': f"{weekly_stats['week_start']} - {weekly_stats['week_end']}",
           'admins_notified': len(email_list),
           'stats': weekly_stats,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Haftalık rapor hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def notify_user_milestone(
   self,
   user_id: str,
   milestone_type: str,
   milestone_value: int,
   details: Optional[Dict] = None
):
   """Kullanıcı milestone bildirimi"""
   try:
       user = User.objects.get(id=user_id)
       logger.info(f"🎉 Milestone bildirimi: {user.email} - {milestone_type}")
       
       # Milestone mesajları
       milestone_messages = {
           'first_query': {
               'title': '🎉 SAPBot\'a Hoş Geldiniz!',
               'message': 'İlk sorunuzu sordunuz. SAP Business One ile ilgili her konuda yardımcı olmaktan mutluluk duyarız.',
               'emoji': '🎉'
           },
           'queries_10': {
               'title': '🔥 10 Sorgu Tamamlandı!',
               'message': '10. sorunuzu tamamladınız. SAPBot\'u aktif kullandığınız için teşekkürler!',
               'emoji': '🔥'
           },
           'queries_50': {
               'title': '⭐ Süper Kullanıcı!',
               'message': '50 sorgu tamamladınız! Artık SAPBot\'un deneyimli bir kullanıcısısınız.',
               'emoji': '⭐'
           },
           'queries_100': {
               'title': '🏆 SAPBot Uzmanı!',
               'message': '100 sorgu milestone\'ına ulaştınız! SAP Business One konusunda gerçek bir uzman oldunuz.',
               'emoji': '🏆'
           },
           'documents_uploaded_1': {
               'title': '📄 İlk Döküman Yüklendi!',
               'message': 'İlk dökümanınızı yüklediniz. SAPBot\'un bilgi tabanına katkıda bulunduğunuz için teşekkürler!',
               'emoji': '📄'
           },
           'consecutive_days_7': {
               'title': '📅 Sadık Kullanıcı!',
               'message': '7 gün üst üste SAPBot\'u kullandınız. Sürekli öğrenme azminiz takdire şayan!',
               'emoji': '📅'
           },
           'feedback_given_5': {
               'title': '💭 Geri Bildirim Şampiyonu!',
               'message': '5 geri bildirim verdiniz. SAPBot\'u geliştirmemize yardım ettiğiniz için teşekkürler!',
               'emoji': '💭'
           }
       }
       
       milestone_info = milestone_messages.get(
           f"{milestone_type}_{milestone_value}",
           milestone_messages.get(milestone_type, {
               'title': '🎯 Yeni Milestone!',
               'message': f'{milestone_type} konusunda {milestone_value} milestone\'ına ulaştınız!',
               'emoji': '🎯'
           })
       )
       
       # Kullanıcı profilini kontrol et
       try:
           user_profile = user.sapbot_profile
           if not user_profile.email_notifications:
               logger.info(f"ℹ️ Kullanıcı email bildirimi kapatmış: {user.email}")
               return {'success': True, 'skipped': 'email_notifications_disabled'}
       except:
           pass  # Profil yoksa devam et
       
       # Email bildirimi
       email_context = {
           'user_name': user.first_name or user.username,
           'milestone_title': milestone_info['title'],
           'milestone_message': milestone_info['message'],
           'milestone_emoji': milestone_info['emoji'],
           'milestone_type': milestone_type,
           'milestone_value': milestone_value,
           'details': details or {}
       }
       
       send_email_notification.delay(
           recipient_email=user.email,
           subject=f"{milestone_info['emoji']} {milestone_info['title']}",
           message=milestone_info['message'],
           template_name='user_milestone',
           context=email_context
       )
       
       # Sistem bildirimi oluştur
       SystemNotification.objects.create(
           title=milestone_info['title'],
           message=milestone_info['message'],
           notification_type='success',
           priority=1,
           is_system_wide=False,
           expires_at=timezone.now() + timedelta(days=7)
       )
       
       # Milestone kullanıcının bildirimlerine ekle
       notification = SystemNotification.objects.create(
           title=milestone_info['title'],
           message=milestone_info['message'],
           notification_type='info',
           priority=2,
           is_system_wide=False,
           expires_at=timezone.now() + timedelta(days=30)
       )
       notification.target_users.add(user)
       
       logger.info(f"✅ Milestone bildirimi gönderildi: {user.email}")
       
       return {
           'success': True,
           'user_email': user.email,
           'milestone_type': milestone_type,
           'milestone_value': milestone_value,
           'notification_sent': True,
           'timestamp': timezone.now().isoformat()
       }
       
   except User.DoesNotExist:
       logger.error(f"❌ Kullanıcı bulunamadı: {user_id}")
       return {'success': False, 'error': 'user_not_found'}
   except Exception as exc:
       logger.error(f"❌ Milestone bildirim hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_password_reset_notification(self, user_email: str, reset_token: str, reset_url: str):
   """Şifre sıfırlama bildirimi"""
   try:
       user = User.objects.get(email=user_email)
       logger.info(f"🔐 Şifre sıfırlama bildirimi: {user_email}")
       
       email_context = {
           'user_name': user.first_name or user.username,
           'reset_url': reset_url,
           'reset_token': reset_token,
           'expiry_hours': 24,
           'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@tunacelik.com.tr')
       }
       
       send_email_notification.delay(
           recipient_email=user_email,
           subject="🔐 SAPBot Şifre Sıfırlama Talebi",
           message=f"Şifre sıfırlama talebiniz alındı. Lütfen aşağıdaki bağlantıyı kullanın:\n\n{reset_url}",
           template_name='password_reset',
           context=email_context
       )
       
       return {
           'success': True,
           'user_email': user_email,
           'notification_sent': True,
           'timestamp': timezone.now().isoformat()
       }
       
   except User.DoesNotExist:
       logger.error(f"❌ Şifre sıfırlama: Kullanıcı bulunamadı - {user_email}")
       return {'success': False, 'error': 'user_not_found'}
   except Exception as exc:
       logger.error(f"❌ Şifre sıfırlama bildirim hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def send_welcome_email(self, user_id: str):
   """Hoş geldin email'i gönder"""
   try:
       user = User.objects.get(id=user_id)
       logger.info(f"👋 Hoş geldin email'i: {user.email}")
       
       email_context = {
           'user_name': user.first_name or user.username,
           'user_email': user.email,
           'login_url': f"{getattr(settings, 'FRONTEND_URL', 'https://sapbot.tunacelik.com.tr')}/login",
           'docs_url': f"{getattr(settings, 'FRONTEND_URL', 'https://sapbot.tunacelik.com.tr')}/docs",
           'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@tunacelik.com.tr'),
           'company_name': 'Tuna Çelik'
       }
       
       send_email_notification.delay(
           recipient_email=user.email,
           subject="👋 SAPBot'a Hoş Geldiniz!",
           message=f"Merhaba {email_context['user_name']},\n\nSAPBot'a hoş geldiniz! SAP Business One konusunda size yardımcı olmaktan mutluluk duyarız.",
           template_name='welcome',
           context=email_context
       )
       
       return {
           'success': True,
           'user_email': user.email,
           'welcome_sent': True,
           'timestamp': timezone.now().isoformat()
       }
       
   except User.DoesNotExist:
       logger.error(f"❌ Hoş geldin email: Kullanıcı bulunamadı - {user_id}")
       return {'success': False, 'error': 'user_not_found'}
   except Exception as exc:
       logger.error(f"❌ Hoş geldin email hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def check_and_send_error_alerts(self):
   """Hata uyarılarını kontrol et ve gönder"""
   try:
       logger.info("🚨 Hata uyarıları kontrol ediliyor...")
       
       # Son 1 saatteki kritik hatalar
       last_hour = timezone.now() - timedelta(hours=1)
       critical_errors = ErrorLog.objects.filter(
           created_at__gte=last_hour,
           error_level='CRITICAL',
           is_resolved=False
       )
       
       critical_count = critical_errors.count()
       
       # Son 1 saatteki toplam hatalar
       total_errors = ErrorLog.objects.filter(
           created_at__gte=last_hour
       ).count()
       
       alerts_sent = []
       
       # Kritik hata uyarısı
       if critical_count > 0:
           error_details = {
               'critical_errors': critical_count,
               'total_errors': total_errors,
               'time_period': '1 saat',
               'error_types': list(critical_errors.values_list('error_type', flat=True).distinct())
           }
           
           notify_system_alert.delay(
               alert_type='critical_errors',
               severity='critical',
               message=f"Son 1 saatte {critical_count} kritik hata tespit edildi!",
               details=error_details,
               notify_channels=['email', 'slack', 'teams']
           )
           
           alerts_sent.append('critical_errors')
       
       # Yüksek hata oranı uyarısı
       if total_errors > 50:  # Saatte 50'den fazla hata
           error_details = {
               'total_errors': total_errors,
               'error_rate': f"{total_errors}/saat",
               'threshold': '50/saat',
               'time_period': '1 saat'
           }
           
           notify_system_alert.delay(
               alert_type='high_error_rate',
               severity='warning',
               message=f"Yüksek hata oranı tespit edildi: {total_errors}/saat",
               details=error_details,
               notify_channels=['email', 'slack']
           )
           
           alerts_sent.append('high_error_rate')
       
       # Tekrarlayan hata pattern'ları
       recurring_errors = ErrorLog.objects.filter(
           created_at__gte=last_hour
       ).values('error_type', 'error_message').annotate(
           count=models.Count('id')
       ).filter(count__gte=5).order_by('-count')
       
       if recurring_errors:
           for error in recurring_errors[:3]:  # En çok tekrar eden 3 hata
               error_details = {
                   'error_type': error['error_type'],
                   'error_message': error['error_message'][:200],
                   'occurrence_count': error['count'],
                   'time_period': '1 saat'
               }
               
               notify_system_alert.delay(
                   alert_type='recurring_error',
                   severity='warning',
                   message=f"Tekrarlayan hata pattern'i tespit edildi: {error['error_type']} ({error['count']} kez)",
                   details=error_details,
                   notify_channels=['email', 'slack']
               )
           
           alerts_sent.append('recurring_errors')
       
       # Sistem performans uyarısı
       slow_queries = QueryAnalytics.objects.filter(
           created_at__gte=last_hour,
           response_time__gt=10  # 10 saniyeden uzun
       ).count()
       
       if slow_queries > 5:
           performance_details = {
               'slow_queries': slow_queries,
               'threshold': '10 saniye',
               'time_period': '1 saat'
           }
           
           notify_system_alert.delay(
               alert_type='performance_degradation',
               severity='warning',
               message=f"Performans düşüşü tespit edildi: {slow_queries} yavaş sorgu",
               details=performance_details,
               notify_channels=['email', 'slack']
           )
           
           alerts_sent.append('performance_issues')
       
       logger.info(f"✅ Hata kontrolü tamamlandı - {len(alerts_sent)} uyarı gönderildi")
       
       return {
           'success': True,
           'alerts_sent': alerts_sent,
           'critical_errors': critical_count,
           'total_errors': total_errors,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Hata kontrolü hatası: {exc}")
       raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=1)
def cleanup_old_notifications(self, days_old: int = 30):
   """Eski bildirimleri temizle"""
   try:
       logger.info(f"🧹 {days_old} günden eski bildirimler temizleniyor...")
       
       cutoff_date = timezone.now() - timedelta(days=days_old)
       
       # Süresi dolmuş bildirimler
       expired_notifications = SystemNotification.objects.filter(
           expires_at__lt=timezone.now()
       )
       expired_count = expired_notifications.count()
       expired_notifications.delete()
       
       # Eski okunmuş bildirimler
       old_read_notifications = SystemNotification.objects.filter(
           created_at__lt=cutoff_date,
           is_read=True
       )
       old_read_count = old_read_notifications.count()
       old_read_notifications.delete()
       
       logger.info(f"✅ {expired_count} süresi dolmuş, {old_read_count} eski okunmuş bildirim silindi")
       
       return {
           'success': True,
           'expired_deleted': expired_count,
           'old_read_deleted': old_read_count,
           'total_deleted': expired_count + old_read_count,
           'timestamp': timezone.now().isoformat()
       }
       
   except Exception as exc:
       logger.error(f"❌ Bildirim temizleme hatası: {exc}")
       raise self.retry(exc=exc)


# Celery beat schedule için notification task'ları
NOTIFICATION_TASKS = {
   'daily-summary-report': {
       'task': 'sapbot_api.tasks.notification_tasks.send_daily_summary_report',
       'schedule': 3600.0 * 24,  # Her gün saat 00:00
       'options': {'queue': 'notifications'}
   },
   'weekly-analytics-report': {
       'task': 'sapbot_api.tasks.notification_tasks.send_weekly_analytics_report',
       'schedule': 3600.0 * 24 * 7,  # Her pazartesi
       'options': {'queue': 'notifications'}
   },
   'error-alerts-check': {
       'task': 'sapbot_api.tasks.notification_tasks.check_and_send_error_alerts',
       'schedule': 3600.0,  # Her saat
       'options': {'queue': 'alerts'}
   },
   'cleanup-old-notifications': {
       'task': 'sapbot_api.tasks.notification_tasks.cleanup_old_notifications',
       'schedule': 3600.0 * 24,  # Her gün
       'options': {'queue': 'cleanup'}
   }
}


# Notification helper functions
def send_user_notification(user_id: str, title: str, message: str, notification_type: str = 'info'):
   """Kullanıcıya bildirim gönder"""
   try:
       user = User.objects.get(id=user_id)
       
       # Sistem bildirimi oluştur
       notification = SystemNotification.objects.create(
           title=title,
           message=message,
           notification_type=notification_type,
           priority=2,
           is_system_wide=False,
           expires_at=timezone.now() + timedelta(days=7)
       )
       notification.target_users.add(user)
       
       # Email bildirimi (eğer kullanıcı istiyorsa)
       try:
           user_profile = user.sapbot_profile
           if user_profile.email_notifications:
               send_email_notification.delay(
                   recipient_email=user.email,
                   subject=f"📢 SAPBot - {title}",
                   message=message,
                   is_html=False
               )
       except:
           pass  # Profil yoksa sadece sistem bildirimi
       
       return True
       
   except User.DoesNotExist:
       logger.error(f"❌ Bildirim gönderme: Kullanıcı bulunamadı - {user_id}")
       return False
   except Exception as e:
       logger.error(f"❌ Bildirim gönderme hatası: {e}")
       return False


def send_admin_alert(title: str, message: str, severity: str = 'warning', details: Dict = None):
   """Admin'lere uyarı gönder"""
   notify_system_alert.delay(
       alert_type='admin_alert',
       severity=severity,
       message=message,
       details=details or {},
       notify_channels=['email', 'slack']
   )
