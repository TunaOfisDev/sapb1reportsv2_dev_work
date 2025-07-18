"""
SAPBot API Notification Service

Bu servis çeşitli bildirim türlerini yönetir:
- Email bildirimleri
- Real-time WebSocket bildirimleri
- System notifications
- User alerts
- Admin notifications
"""

import logging
import smtplib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
from dataclasses import dataclass, asdict
from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import (
    SystemNotification,
    DocumentSource
)
from ..utils.helpers import format_response_time
from ..utils.cache_utils import system_cache

User = get_user_model()
logger = logging.getLogger(__name__)


@dataclass
class NotificationData:
    """Bildirim veri yapısı"""
    recipient: str
    subject: str
    message: str
    notification_type: str = 'info'
    priority: int = 2
    metadata: Dict[str, Any] = None
    template: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.context is None:
            self.context = {}


class EmailService:
    """Email bildirim servisi"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'EMAIL_HOST', 'localhost')
        self.smtp_port = getattr(settings, 'EMAIL_PORT', 587)
        self.smtp_username = getattr(settings, 'EMAIL_HOST_USER', '')
        self.smtp_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tunacelik.com.tr')
        
    def send_email(
        self,
        recipient: str,
        subject: str,
        message: str,
        html_content: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """Email gönder"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Metin içerik
            text_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML içerik
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Ekler
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # SMTP bağlantısı ve gönderim
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email başarıyla gönderildi: {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Email gönderme hatası: {e}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict):
        """Email'e dosya eki ekle"""
        try:
            with open(attachment['path'], 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Dosya eki ekleme hatası: {e}")
    
    def send_template_email(
        self,
        recipient: str,
        template_name: str,
        context: Dict[str, Any],
        subject: str = None
    ) -> bool:
        """Template ile email gönder"""
        try:
            # HTML template render et
            html_content = render_to_string(f'sapbot_api/emails/{template_name}.html', context)
            
            # Text template varsa render et
            try:
                text_content = render_to_string(f'sapbot_api/emails/{template_name}.txt', context)
            except:
                # HTML'den basit text oluştur
                import re
                text_content = re.sub('<[^<]+?>', '', html_content)
            
            # Subject template'den al
            if not subject:
                try:
                    subject = render_to_string(f'sapbot_api/emails/{template_name}_subject.txt', context).strip()
                except:
                    subject = f"SAPBot Bildirimi - {template_name}"
            
            return self.send_email(recipient, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Template email gönderme hatası: {e}")
            return False


class WebSocketService:
    """WebSocket real-time bildirim servisi"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_notification(
        self,
        user_id: str,
        notification_type: str,
        message: str,
        data: Dict[str, Any] = None
    ) -> bool:
        """Kullanıcıya real-time bildirim gönder"""
        try:
            if not self.channel_layer:
                logger.warning("Channel layer bulunamadı, WebSocket bildirimi gönderilemedi")
                return False
            
            notification_data = {
                'type': 'notification',
                'notification_type': notification_type,
                'message': message,
                'timestamp': timezone.now().isoformat(),
                'data': data or {}
            }
            
            # Kullanıcının group'una gönder
            group_name = f"user_{user_id}"
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'notification': notification_data
                }
            )
            
            logger.info(f"WebSocket bildirimi gönderildi: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket bildirim hatası: {e}")
            return False
    
    def send_system_broadcast(
        self,
        message: str,
        notification_type: str = 'info',
        data: Dict[str, Any] = None
    ) -> bool:
        """Sistem geneli broadcast bildirim"""
        try:
            if not self.channel_layer:
                return False
            
            broadcast_data = {
                'type': 'system_broadcast',
                'notification_type': notification_type,
                'message': message,
                'timestamp': timezone.now().isoformat(),
                'data': data or {}
            }
            
            async_to_sync(self.channel_layer.group_send)(
                'system_broadcast',
                {
                    'type': 'send_broadcast',
                    'broadcast': broadcast_data
                }
            )
            
            logger.info("Sistem broadcast bildirimi gönderildi")
            return True
            
        except Exception as e:
            logger.error(f"Sistem broadcast hatası: {e}")
            return False


class SystemNotificationService:
    """Sistem bildirimi servisi"""
    
    def __init__(self):
        self.websocket_service = WebSocketService()
    
    def create_notification(
        self,
        title: str,
        message: str,
        notification_type: str = 'info',
        priority: int = 2,
        target_users: List[User] = None, # type: ignore
        is_system_wide: bool = False,
        expires_at: datetime = None,
        action_url: str = None,
        action_text: str = None
    ) -> SystemNotification:
        """Sistem bildirimi oluştur"""
        try:
            notification = SystemNotification.objects.create(
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                is_system_wide=is_system_wide,
                expires_at=expires_at,
                action_url=action_url,
                action_text=action_text
            )
            
            # Hedef kullanıcıları ekle
            if target_users:
                notification.target_users.set(target_users)
            
            # Real-time bildirim gönder
            if is_system_wide:
                self.websocket_service.send_system_broadcast(
                    message=title,
                    notification_type=notification_type,
                    data={
                        'notification_id': str(notification.id),
                        'message': message,
                        'action_url': action_url,
                        'action_text': action_text
                    }
                )
            elif target_users:
                for user in target_users:
                    self.websocket_service.send_notification(
                        user_id=str(user.id),
                        notification_type=notification_type,
                        message=title,
                        data={
                            'notification_id': str(notification.id),
                            'message': message,
                            'action_url': action_url,
                            'action_text': action_text
                        }
                    )
            
            logger.info(f"Sistem bildirimi oluşturuldu: {notification.id}")
            return notification
            
        except Exception as e:
            logger.error(f"Sistem bildirimi oluşturma hatası: {e}")
            raise
    
    def mark_as_read(self, notification_id: str, user: User = None) -> bool:# type: ignore
        """Bildirimi okundu olarak işaretle"""
        try:
            notification = SystemNotification.objects.get(id=notification_id)
            
            # Sistem geneli bildirimse veya kullanıcı hedef listesindeyse
            if notification.is_system_wide or (user and user in notification.target_users.all()):
                notification.is_read = True
                notification.save()
                return True
            
            return False
            
        except SystemNotification.DoesNotExist:
            logger.error(f"Bildirim bulunamadı: {notification_id}")
            return False
        except Exception as e:
            logger.error(f"Bildirim okundu işaretleme hatası: {e}")
            return False
    
    def get_user_notifications(
        self,
        user: User, # type: ignore
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Kullanıcı bildirimlerini getir"""
        try:
            queryset = SystemNotification.objects.filter(
                models.Q(is_system_wide=True) | models.Q(target_users=user) # type: ignore
            ).filter(
                is_active=True
            ).order_by('-created_at')
            
            # Sadece okunmamışlar
            if unread_only:
                queryset = queryset.filter(is_read=False)
            
            # Süresi dolmamışlar
            now = timezone.now()
            queryset = queryset.filter(
                models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
            )
            
            notifications = []
            for notification in queryset[:limit]:
                notifications.append({
                    'id': str(notification.id),
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'priority': notification.priority,
                    'is_read': notification.is_read,
                    'action_url': notification.action_url,
                    'action_text': notification.action_text,
                    'created_at': notification.created_at.isoformat(),
                    'expires_at': notification.expires_at.isoformat() if notification.expires_at else None
                })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Kullanıcı bildirimleri getirme hatası: {e}")
            return []


class NotificationTemplateService:
    """Bildirim template servisi"""
    
    TEMPLATES = {
        'document_processed': {
            'subject': 'Döküman İşleme Tamamlandı - {document_title}',
            'email_template': 'document_processed',
            'default_message': 'Yüklediğiniz döküman başarıyla işlendi.'
        },
        'document_failed': {
            'subject': 'Döküman İşleme Başarısız - {document_title}',
            'email_template': 'document_failed',
            'default_message': 'Döküman işleme sırasında hata oluştu.'
        },
        'system_maintenance': {
            'subject': 'Sistem Bakım Bildirimi',
            'email_template': 'system_maintenance',
            'default_message': 'Sistem bakım çalışması planlandı.'
        },
        'security_alert': {
            'subject': 'Güvenlik Uyarısı - SAPBot',
            'email_template': 'security_alert',
            'default_message': 'Hesabınızda güvenlik ile ilgili bir aktivite tespit edildi.'
        },
        'welcome': {
            'subject': 'SAPBot\'a Hoş Geldiniz!',
            'email_template': 'welcome',
            'default_message': 'SAPBot AI asistanına hoş geldiniz!'
        },
        'password_reset': {
            'subject': 'Şifre Sıfırlama - SAPBot',
            'email_template': 'password_reset',
            'default_message': 'Şifre sıfırlama isteğiniz alındı.'
        },
        'quota_exceeded': {
            'subject': 'Kullanım Kotası Aşıldı',
            'email_template': 'quota_exceeded',
            'default_message': 'Günlük kullanım kotanız aşıldı.'
        },
        'high_error_rate': {
            'subject': 'Yüksek Hata Oranı Tespit Edildi',
            'email_template': 'high_error_rate',
            'default_message': 'Sistemde yüksek hata oranı tespit edildi.'
        }
    }
    
    @classmethod
    def get_template_data(cls, template_name: str) -> Dict[str, str]:
        """Template verilerini getir"""
        return cls.TEMPLATES.get(template_name, {})
    
    @classmethod
    def render_template_message(cls, template_name: str, context: Dict[str, Any]) -> str:
        """Template mesajını render et"""
        template_data = cls.get_template_data(template_name)
        message = template_data.get('default_message', 'Bildirim')
        
        try:
            return message.format(**context)
        except (KeyError, ValueError):
            return message
    
    @classmethod
    def render_template_subject(cls, template_name: str, context: Dict[str, Any]) -> str:
        """Template subject'ini render et"""
        template_data = cls.get_template_data(template_name)
        subject = template_data.get('subject', 'SAPBot Bildirimi')
        
        try:
            return subject.format(**context)
        except (KeyError, ValueError):
            return subject


class NotificationService:
    """Ana bildirim servisi - tüm bildirim türlerini koordine eder"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.websocket_service = WebSocketService()
        self.system_service = SystemNotificationService()
        self.template_service = NotificationTemplateService()
    
    def send_notification(
        self,
        notification_data: NotificationData,
        channels: List[str] = None
    ) -> Dict[str, bool]:
        """Çoklu kanal bildirim gönder"""
        if channels is None:
            channels = ['email', 'websocket']
        
        results = {}
        
        try:
            # Email bildirimi
            if 'email' in channels:
                if notification_data.template:
                    results['email'] = self.email_service.send_template_email(
                        recipient=notification_data.recipient,
                        template_name=notification_data.template,
                        context=notification_data.context,
                        subject=notification_data.subject
                    )
                else:
                    results['email'] = self.email_service.send_email(
                        recipient=notification_data.recipient,
                        subject=notification_data.subject,
                        message=notification_data.message
                    )
            
            # WebSocket bildirimi
            if 'websocket' in channels:
                # Email'den user ID çıkar
                try:
                    user = User.objects.get(email=notification_data.recipient)
                    results['websocket'] = self.websocket_service.send_notification(
                        user_id=str(user.id),
                        notification_type=notification_data.notification_type,
                        message=notification_data.message,
                        data=notification_data.metadata
                    )
                except User.DoesNotExist:
                    results['websocket'] = False
            
            # Sistem bildirimi
            if 'system' in channels:
                try:
                    user = User.objects.get(email=notification_data.recipient)
                    notification = self.system_service.create_notification(
                        title=notification_data.subject,
                        message=notification_data.message,
                        notification_type=notification_data.notification_type,
                        priority=notification_data.priority,
                        target_users=[user]
                    )
                    results['system'] = bool(notification)
                except User.DoesNotExist:
                    results['system'] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Bildirim gönderme hatası: {e}")
            return {channel: False for channel in channels}
    
    def send_template_notification(
        self,
        template_name: str,
        recipient: str,
        context: Dict[str, Any],
        channels: List[str] = None
    ) -> Dict[str, bool]:
        """Template ile bildirim gönder"""
        try:
            # Template verilerini al
            template_data = self.template_service.get_template_data(template_name)
            
            if not template_data:
                logger.error(f"Template bulunamadı: {template_name}")
                return {}
            
            # Notification data oluştur
            notification_data = NotificationData(
                recipient=recipient,
                subject=self.template_service.render_template_subject(template_name, context),
                message=self.template_service.render_template_message(template_name, context),
                template=template_data.get('email_template'),
                context=context
            )
            
            return self.send_notification(notification_data, channels)
            
        except Exception as e:
            logger.error(f"Template bildirim gönderme hatası: {e}")
            return {}
    
    def notify_document_processed(self, document: DocumentSource, user: User): # type: ignore
        """Döküman işleme tamamlandı bildirimi"""
        context = {
            'user_name': user.get_full_name() or user.email,
            'document_title': document.title,
            'document_type': document.get_document_type_display(),
            'processed_at': document.processed_at.strftime('%d.%m.%Y %H:%M') if document.processed_at else '',
            'chunk_count': document.chunk_count,
            'file_size': f"{document.file_size_mb:.1f} MB" if document.file_size else "N/A"
        }
        
        return self.send_template_notification(
            template_name='document_processed',
            recipient=user.email,
            context=context,
            channels=['email', 'websocket', 'system']
        )
    
    def notify_document_failed(self, document: DocumentSource, user: User, error_message: str): # type: ignore
        """Döküman işleme başarısız bildirimi"""
        context = {
            'user_name': user.get_full_name() or user.email,
            'document_title': document.title,
            'error_message': error_message,
            'upload_time': document.created_at.strftime('%d.%m.%Y %H:%M')
        }
        
        return self.send_template_notification(
            template_name='document_failed',
            recipient=user.email,
            context=context,
            channels=['email', 'websocket', 'system']
        )
    
    def notify_system_maintenance(self, start_time: datetime, end_time: datetime, description: str):
        """Sistem bakım bildirimi"""
        context = {
            'start_time': start_time.strftime('%d.%m.%Y %H:%M'),
            'end_time': end_time.strftime('%d.%m.%Y %H:%M'),
            'duration': format_response_time((end_time - start_time).total_seconds()),
            'description': description
        }
        
        # Tüm aktif kullanıcılara gönder
        active_users = User.objects.filter(is_active=True)
        results = []
        
        for user in active_users:
            result = self.send_template_notification(
                template_name='system_maintenance',
                recipient=user.email,
                context=context,
                channels=['email', 'system']
            )
            results.append(result)
        
        # Sistem broadcast
        self.websocket_service.send_system_broadcast(
            message=f"Sistem bakımı: {start_time.strftime('%d.%m.%Y %H:%M')} - {end_time.strftime('%H:%M')}",
            notification_type='warning',
            data=context
        )
        
        return results
    
    def notify_security_alert(self, user: User, alert_type: str, details: Dict[str, Any]): # type: ignore
        """Güvenlik uyarısı bildirimi"""
        context = {
            'user_name': user.get_full_name() or user.email,
            'alert_type': alert_type,
            'timestamp': timezone.now().strftime('%d.%m.%Y %H:%M:%S'),
            'ip_address': details.get('ip_address', 'Bilinmiyor'),
            'user_agent': details.get('user_agent', 'Bilinmiyor')[:100],
            'details': details
        }
        
        return self.send_template_notification(
            template_name='security_alert',
            recipient=user.email,
            context=context,
            channels=['email', 'websocket', 'system']
        )
    
    def notify_welcome_user(self, user: User): # type: ignore
        """Yeni kullanıcı hoş geldin bildirimi"""
        context = {
            'user_name': user.get_full_name() or user.email,
            'login_url': f"{settings.FRONTEND_URL}/login" if hasattr(settings, 'FRONTEND_URL') else '#',
            'help_url': f"{settings.FRONTEND_URL}/help" if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        return self.send_template_notification(
            template_name='welcome',
            recipient=user.email,
            context=context,
            channels=['email']
        )
    
    def notify_quota_exceeded(self, user: User, quota_type: str, current_usage: int, limit: int): # type: ignore
        """Kota aşım bildirimi"""
        context = {
            'user_name': user.get_full_name() or user.email,
            'quota_type': quota_type,
            'current_usage': current_usage,
            'limit': limit,
            'percentage': round((current_usage / limit) * 100, 1) if limit > 0 else 0
        }
        
        return self.send_template_notification(
            template_name='quota_exceeded',
            recipient=user.email,
            context=context,
            channels=['email', 'websocket', 'system']
        )
    
    def notify_admin_high_error_rate(self, error_rate: float, time_period: str):
        """Yöneticilere yüksek hata oranı bildirimi"""
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        
        context = {
            'error_rate': f"{error_rate:.1f}%",
            'time_period': time_period,
            'timestamp': timezone.now().strftime('%d.%m.%Y %H:%M:%S'),
            'dashboard_url': f"{settings.FRONTEND_URL}/admin/analytics" if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        results = []
        for admin in admin_users:
            context['admin_name'] = admin.get_full_name() or admin.email
            result = self.send_template_notification(
                template_name='high_error_rate',
                recipient=admin.email,
                context=context,
                channels=['email', 'system']
            )
            results.append(result)
        
        return results


class NotificationQueue:
    """Bildirim kuyruğu - asenkron bildirim işleme"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.queue_key = "notification_queue"
    
    def enqueue_notification(
        self,
        notification_data: NotificationData,
        channels: List[str] = None,
        priority: int = 2,
        delay_seconds: int = 0
    ):
        """Bildirimi kuyruğa ekle"""
        try:
            queue_item = {
                'notification_data': asdict(notification_data),
                'channels': channels or ['email'],
                'priority': priority,
                'scheduled_at': (timezone.now() + timedelta(seconds=delay_seconds)).isoformat(),
                'created_at': timezone.now().isoformat(),
                'retry_count': 0,
                'max_retries': 3
            }
            
            # Redis kuyruğuna ekle (öncelik sırasına göre)
            system_cache.redis_client.zadd(
                self.queue_key,
                {json.dumps(queue_item): priority}
            )
            
            logger.info(f"Bildirim kuyruğa eklendi: {notification_data.recipient}")
            
        except Exception as e:
            logger.error(f"Bildirim kuyruğa ekleme hatası: {e}")
    
    def process_queue(self, batch_size: int = 10) -> int:
        """Kuyruktan bildirimleri işle"""
        try:
            processed_count = 0
            now = timezone.now()
            
            # Kuyruktaki öğeleri al (öncelik sırasına göre)
            queue_items = system_cache.redis_client.zrange(
                self.queue_key, 0, batch_size - 1, withscores=True
            )
            
            for item_json, priority in queue_items:
                try:
                    item = json.loads(item_json)
                    scheduled_at = datetime.fromisoformat(item['scheduled_at'])
                    
                    # Zamanı gelmişse işle
                    if scheduled_at <= now:
                        notification_data = NotificationData(**item['notification_data'])
                        channels = item['channels']
                        
                        # Bildirimi gönder
                        results = self.notification_service.send_notification(
                            notification_data, channels
                        )
                        
                        # Başarılıysa kuyruktan kaldır
                        if any(results.values()):
                            system_cache.redis_client.zrem(self.queue_key, item_json)
                            processed_count += 1
                        else:
                            # Başarısızsa retry sayısını artır
                            item['retry_count'] += 1
                            if item['retry_count'] >= item['max_retries']:
                                # Max retry aşıldıysa kaldır
                                system_cache.redis_client.zrem(self.queue_key, item_json)
                                logger.error(f"Bildirim max retry aşıldı: {notification_data.recipient}")
                            else:
                                # Tekrar dene (5 dakika sonra)
                                item['scheduled_at'] = (now + timedelta(minutes=5)).isoformat()
                                system_cache.redis_client.zrem(self.queue_key, item_json)
                                system_cache.redis_client.zadd(
                                    self.queue_key,
                                    {json.dumps(item): priority}
                                )
                
                except Exception as e:
                    logger.error(f"Kuyruk öğesi işleme hatası: {e}")
                    continue
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Kuyruk işleme hatası: {e}")
            return 0
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Kuyruk istatistikleri"""
        try:
            total_count = system_cache.redis_client.zcard(self.queue_key)
            
            # Öncelik dağılımı
            priority_distribution = {}
            queue_items = system_cache.redis_client.zrange(
                self.queue_key, 0, -1, withscores=True
            )
            
            for item_json, priority in queue_items:
                priority = int(priority)
                priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            
            return {
                'total_count': total_count,
                'priority_distribution': priority_distribution,
                'queue_size_bytes': len(str(queue_items))
            }
            
        except Exception as e:
            logger.error(f"Kuyruk istatistik hatası: {e}")
            return {'total_count': 0, 'priority_distribution': {}, 'queue_size_bytes': 0}


# Singleton instances
notification_service = NotificationService()
notification_queue = NotificationQueue()


# Utility functions
def send_immediate_notification(
   recipient: str,
   subject: str,
   message: str,
   notification_type: str = 'info',
   channels: List[str] = None
) -> Dict[str, bool]:
   """Anında bildirim gönder"""
   notification_data = NotificationData(
       recipient=recipient,
       subject=subject,
       message=message,
       notification_type=notification_type
   )
   
   return notification_service.send_notification(notification_data, channels)


def send_delayed_notification(
   recipient: str,
   subject: str,
   message: str,
   delay_minutes: int = 5,
   notification_type: str = 'info',
   channels: List[str] = None
) -> None:
   """Gecikmeli bildirim gönder"""
   notification_data = NotificationData(
       recipient=recipient,
       subject=subject,
       message=message,
       notification_type=notification_type
   )
   
   notification_queue.enqueue_notification(
       notification_data,
       channels,
       delay_seconds=delay_minutes * 60
   )


def send_bulk_notification(
   recipients: List[str],
   subject: str,
   message: str,
   template_name: str = None,
   context: Dict[str, Any] = None,
   channels: List[str] = None
) -> List[Dict[str, bool]]:
   """Toplu bildirim gönder"""
   results = []
   
   for recipient in recipients:
       if template_name:
           result = notification_service.send_template_notification(
               template_name=template_name,
               recipient=recipient,
               context=context or {},
               channels=channels
           )
       else:
           notification_data = NotificationData(
               recipient=recipient,
               subject=subject,
               message=message
           )
           result = notification_service.send_notification(notification_data, channels)
       
       results.append(result)
   
   return results


def notify_system_health_issue(
   component: str,
   status: str,
   details: Dict[str, Any]
) -> None:
   """Sistem sağlık sorunu bildirimi"""
   admin_users = User.objects.filter(is_staff=True, is_active=True)
   
   subject = f"Sistem Sağlık Uyarısı - {component}"
   message = f"Bileşen: {component}\nDurum: {status}\nDetaylar: {details}"
   
   for admin in admin_users:
       send_immediate_notification(
           recipient=admin.email,
           subject=subject,
           message=message,
           notification_type='error',
           channels=['email', 'websocket']
       )


def notify_performance_issue(
   metric_name: str,
   current_value: float,
   threshold: float,
   time_period: str
) -> None:
   """Performans sorunu bildirimi"""
   admin_users = User.objects.filter(is_staff=True, is_active=True)
   
   subject = f"Performans Uyarısı - {metric_name}"
   message = f"""
Metrik: {metric_name}
Mevcut Değer: {current_value}
Eşik Değer: {threshold}
Zaman Periyodu: {time_period}
Durum: Eşik değer aşıldı
"""
   
   for admin in admin_users:
       send_immediate_notification(
           recipient=admin.email,
           subject=subject,
           message=message,
           notification_type='warning',
           channels=['email', 'system']
       )


def create_system_announcement(
   title: str,
   message: str,
   priority: int = 2,
   expires_hours: int = 24
) -> SystemNotification:
   """Sistem duyurusu oluştur"""
   expires_at = timezone.now() + timedelta(hours=expires_hours)
   
   return notification_service.system_service.create_notification(
       title=title,
       message=message,
       notification_type='info',
       priority=priority,
       is_system_wide=True,
       expires_at=expires_at
   )


class NotificationMetrics:
   """Bildirim metrikleri"""
   
   @staticmethod
   def get_notification_stats(days: int = 30) -> Dict[str, Any]:
       """Bildirim istatistikleri"""
       try:
           from datetime import datetime, timedelta
           from django.db import models
           
           end_date = timezone.now()
           start_date = end_date - timedelta(days=days)
           
           # Sistem bildirimi istatistikleri
           system_notifications = SystemNotification.objects.filter(
               created_at__gte=start_date,
               created_at__lte=end_date
           )
           
           stats = {
               'total_notifications': system_notifications.count(),
               'by_type': dict(system_notifications.values('notification_type').annotate(
                   count=models.Count('id')
               ).values_list('notification_type', 'count')),
               'by_priority': dict(system_notifications.values('priority').annotate(
                   count=models.Count('id')
               ).values_list('priority', 'count')),
               'read_rate': 0,
               'avg_response_time': 0
           }
           
           # Okunma oranı
           total_count = stats['total_notifications']
           if total_count > 0:
               read_count = system_notifications.filter(is_read=True).count()
               stats['read_rate'] = round((read_count / total_count) * 100, 1)
           
           # Cache'den email istatistikleri al
           email_stats = system_cache.get('email_notification_stats') or {}
           stats.update({
               'email_sent': email_stats.get('sent_count', 0),
               'email_failed': email_stats.get('failed_count', 0),
               'email_success_rate': email_stats.get('success_rate', 0)
           })
           
           return stats
           
       except Exception as e:
           logger.error(f"Bildirim istatistik hatası: {e}")
           return {}
   
   @staticmethod
   def update_email_stats(sent: bool):
       """Email istatistiklerini güncelle"""
       try:
           stats = system_cache.get('email_notification_stats') or {
               'sent_count': 0,
               'failed_count': 0,
               'success_rate': 0
           }
           
           if sent:
               stats['sent_count'] += 1
           else:
               stats['failed_count'] += 1
           
           total = stats['sent_count'] + stats['failed_count']
           if total > 0:
               stats['success_rate'] = round((stats['sent_count'] / total) * 100, 1)
           
           system_cache.set('email_notification_stats', stats, 86400)  # 24 saat
           
       except Exception as e:
           logger.error(f"Email istatistik güncelleme hatası: {e}")


class NotificationHealthCheck:
   """Bildirim sistemi sağlık kontrolü"""
   
   @staticmethod
   def check_email_service() -> Dict[str, Any]:
       """Email servis sağlık kontrolü"""
       try:
           email_service = EmailService()
           
           # Test email gönderim (kendine)
           test_result = email_service.send_email(
               recipient=email_service.from_email,
               subject="SAPBot Email Service Health Check",
               message="Bu test mesajıdır. Email servisi çalışıyor."
           )
           
           return {
               'service': 'email',
               'status': 'healthy' if test_result else 'unhealthy',
               'response_time': 0,  # TODO: Measure actual response time
               'last_check': timezone.now().isoformat()
           }
           
       except Exception as e:
           return {
               'service': 'email',
               'status': 'error',
               'error': str(e),
               'last_check': timezone.now().isoformat()
           }
   
   @staticmethod
   def check_websocket_service() -> Dict[str, Any]:
       """WebSocket servis sağlık kontrolü"""
       try:
           websocket_service = WebSocketService()
           
           # Channel layer kontrolü
           has_channel_layer = websocket_service.channel_layer is not None
           
           return {
               'service': 'websocket',
               'status': 'healthy' if has_channel_layer else 'unhealthy',
               'channel_layer_available': has_channel_layer,
               'last_check': timezone.now().isoformat()
           }
           
       except Exception as e:
           return {
               'service': 'websocket',
               'status': 'error',
               'error': str(e),
               'last_check': timezone.now().isoformat()
           }
   
   @staticmethod
   def check_notification_queue() -> Dict[str, Any]:
       """Bildirim kuyruğu sağlık kontrolü"""
       try:
           queue_stats = notification_queue.get_queue_stats()
           
           # Kuyruk çok doluysa uyarı
           queue_size = queue_stats.get('total_count', 0)
           status = 'healthy'
           
           if queue_size > 1000:
               status = 'warning'
           elif queue_size > 5000:
               status = 'critical'
           
           return {
               'service': 'notification_queue',
               'status': status,
               'queue_size': queue_size,
               'stats': queue_stats,
               'last_check': timezone.now().isoformat()
           }
           
       except Exception as e:
           return {
               'service': 'notification_queue',
               'status': 'error',
               'error': str(e),
               'last_check': timezone.now().isoformat()
           }
   
   @staticmethod
   def get_overall_health() -> Dict[str, Any]:
       """Genel sağlık durumu"""
       checks = [
           NotificationHealthCheck.check_email_service(),
           NotificationHealthCheck.check_websocket_service(),
           NotificationHealthCheck.check_notification_queue()
       ]
       
       # Genel durum hesapla
       healthy_count = sum(1 for check in checks if check['status'] == 'healthy')
       warning_count = sum(1 for check in checks if check['status'] == 'warning')
       error_count = sum(1 for check in checks if check['status'] in ['unhealthy', 'error', 'critical'])
       
       if error_count > 0:
           overall_status = 'unhealthy'
       elif warning_count > 0:
           overall_status = 'warning'
       else:
           overall_status = 'healthy'
       
       return {
           'overall_status': overall_status,
           'services': checks,
           'summary': {
               'healthy': healthy_count,
               'warning': warning_count,
               'error': error_count,
               'total': len(checks)
           },
           'last_check': timezone.now().isoformat()
       }


# Event-driven notification triggers
def on_document_processed(sender, **kwargs):
   """Döküman işlendiğinde bildirim gönder"""
   document = kwargs.get('document')
   user = kwargs.get('user')
   
   if document and user:
       notification_service.notify_document_processed(document, user)


def on_document_failed(sender, **kwargs):
   """Döküman işleme başarısız olduğunda bildirim gönder"""
   document = kwargs.get('document')
   user = kwargs.get('user')
   error = kwargs.get('error', 'Bilinmeyen hata')
   
   if document and user:
       notification_service.notify_document_failed(document, user, str(error)) # type: ignore


def on_high_error_rate(sender, **kwargs):
   """Yüksek hata oranı tespit edildiğinde bildirim gönder"""
   error_rate = kwargs.get('error_rate', 0)
   time_period = kwargs.get('time_period', '1 hour')
   
   if error_rate > 10:  # %10'dan fazla hata oranı
       notification_service.notify_admin_high_error_rate(error_rate, time_period)


def on_user_registered(sender, **kwargs):
   """Yeni kullanıcı kaydolduğunda hoş geldin bildirimi"""
   user = kwargs.get('user')
   
   if user:
       notification_service.notify_welcome_user(user)


def on_security_event(sender, **kwargs):
   """Güvenlik olayında bildirim gönder"""
   user = kwargs.get('user')
   event_type = kwargs.get('event_type')
   details = kwargs.get('details', {})
   
   if user and event_type:
       notification_service.notify_security_alert(user, event_type, details) # type: ignore


# Cleanup functions
def cleanup_old_notifications(days: int = 90):
   """Eski bildirimleri temizle"""
   try:
       cutoff_date = timezone.now() - timedelta(days=days)
       
       deleted_count = SystemNotification.objects.filter(
           created_at__lt=cutoff_date,
           is_read=True
       ).delete()[0]
       
       logger.info(f"Eski bildirimler temizlendi: {deleted_count}")
       return deleted_count
       
   except Exception as e:
       logger.error(f"Bildirim temizleme hatası: {e}")
       return 0


def cleanup_notification_queue():
   """Bildirim kuyruğunu temizle (başarısız öğeler)"""
   try:
       # 24 saatten eski öğeleri kaldır
       cutoff_time = timezone.now() - timedelta(hours=24)
       
       queue_items = system_cache.redis_client.zrange(
           notification_queue.queue_key, 0, -1, withscores=True
       )
       
       cleaned_count = 0
       for item_json, priority in queue_items:
           try:
               item = json.loads(item_json)
               created_at = datetime.fromisoformat(item['created_at'])
               
               if created_at < cutoff_time:
                   system_cache.redis_client.zrem(notification_queue.queue_key, item_json)
                   cleaned_count += 1
                   
           except Exception:
               # Bozuk öğeyi kaldır
               system_cache.redis_client.zrem(notification_queue.queue_key, item_json)
               cleaned_count += 1
       
       logger.info(f"Bildirim kuyruğu temizlendi: {cleaned_count} öğe")
       return cleaned_count
       
   except Exception as e:
       logger.error(f"Kuyruk temizleme hatası: {e}")
       return 0


# Auto-monitoring functions
def monitor_notification_health():
   """Bildirim sistemi sağlığını izle"""
   try:
       health_status = NotificationHealthCheck.get_overall_health()
       
       # Sağlıksız durumda admin'lere bildir
       if health_status['overall_status'] in ['unhealthy', 'warning']:
           admin_users = User.objects.filter(is_staff=True, is_active=True)
           
           for admin in admin_users:
               send_immediate_notification(
                   recipient=admin.email,
                   subject="SAPBot Bildirim Sistemi Uyarısı",
                   message=f"Bildirim sistemi durumu: {health_status['overall_status']}\n\nDetaylar: {json.dumps(health_status, indent=2, ensure_ascii=False)}",
                   notification_type='warning' if health_status['overall_status'] == 'warning' else 'error',
                   channels=['email']
               )
       
       # Sağlık durumunu cache'le
       system_cache.set('notification_system_health', health_status, 300)  # 5 dakika
       
       return health_status
       
   except Exception as e:
       logger.error(f"Bildirim sağlık izleme hatası: {e}")
       return None


# Performance optimization
class NotificationBatcher:
   """Bildirim toplu işleme"""
   
   def __init__(self, batch_size: int = 50, flush_interval: int = 60):
       self.batch_size = batch_size
       self.flush_interval = flush_interval
       self.batch = []
       self.last_flush = timezone.now()
   
   def add_notification(self, notification_data: NotificationData, channels: List[str] = None):
       """Bildirimi batch'e ekle"""
       self.batch.append({
           'notification_data': notification_data,
           'channels': channels or ['email']
       })
       
       # Batch dolu veya zaman aşımı varsa flush et
       if (len(self.batch) >= self.batch_size or 
           (timezone.now() - self.last_flush).seconds >= self.flush_interval):
           self.flush_batch()
   
   def flush_batch(self):
       """Batch'i işle"""
       if not self.batch:
           return
       
       try:
           # Toplu işleme
           for item in self.batch:
               notification_service.send_notification(
                   item['notification_data'],
                   item['channels']
               )
           
           logger.info(f"Bildirim batch işlendi: {len(self.batch)} öğe")
           
       except Exception as e:
           logger.error(f"Batch işleme hatası: {e}")
       finally:
           self.batch.clear()
           self.last_flush = timezone.now()


# Global batcher instance
notification_batcher = NotificationBatcher()