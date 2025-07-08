# File: backend/mailservice/services/report_orchestrator/system_alert_service.py

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from authcentral.models import Department
from mailservice.models.models import MailLog
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SystemAlertService:
    """
    Bilgi_Sistem departmanına sistemsel uyarılar göndermek için servis sınıfı.
    Özellikle rapor başarısızlıkları gibi durumlarda çağrılır.
    """

    def get_recipients(self):
        try:
            department = Department.objects.get(name="Bilgi_Sistem")
            users = User.objects.filter(departments=department, is_active=True)
            return list(users.values_list('email', flat=True))
        except Department.DoesNotExist:
            logger.warning("Bilgi_Sistem departmanı bulunamadı.")
            return []

    def send_alert(self, api_name: str, error_message: str, report_context: dict = None):
        mail_log = None
        try:
            recipients = self.get_recipients()
            if not recipients:
                raise ValueError("Uyarı gönderilecek kişi bulunamadı.")

            subject = f"[UYARI] {api_name} raporu başarısız oldu"
            template_path = 'mailservice/report_orchestrator/failure_notification/report_failure_email.html'

            # Template için context
            context = {
                "api_name": api_name,
                "error_message": error_message,
                "timestamp": timezone.localtime().strftime('%d.%m.%Y %H:%M'),
                **(report_context or {}),
            }

            mail_log = MailLog.objects.create(
                mail_type='Sistem Uyarısı',
                subject=subject,
                recipients=recipients,
                sender=settings.DEFAULT_FROM_EMAIL,
                created_by=None,
                created_by_email=None,
                has_attachments=False,
                related_object_type=api_name,
                related_object_id=None,
                status='PENDING'
            )

            logger.info(f"[MAIL_ALERT] Şablon render ediliyor: {template_path}")
            html_content = render_to_string(template_path, context)

            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)

            mail_log.status = 'SENT'
            mail_log.sent_at = timezone.now()
            mail_log.save()
            logger.info(f"[MAIL_ALERT] {api_name} uyarı maili gönderildi.")
            return True

        except Exception as e:
            logger.error(f"[MAIL_ALERT_ERROR] {api_name} için mail gönderimi başarısız: {str(e)}")
            if mail_log:
                mail_log.status = 'FAILED'
                mail_log.error_message = str(e)
                mail_log.save()
            return False
