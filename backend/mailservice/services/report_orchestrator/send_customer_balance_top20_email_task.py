# backend/mailservice/services/send_customer_balance_top20_email_task.py

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from authcentral.models import Department
from django.utils.timezone import localtime
from mailservice.models.models import MailLog

User = get_user_model()


class CustomerBalanceTop20MailService:
    """Top 20 müşteri bakiyesi için günlük özet mail servisi"""

    def get_mail_recipients(self):
        try:
            department = Department.objects.get(name="TotalRisk_Gunluk_Email")
            users = User.objects.filter(departments=department, is_active=True)
            return list(users.values_list('email', flat=True))
        except Department.DoesNotExist:
            return []

    def send_mail(self, context: dict, report_date: str):
        mail_log = None
        try:
            recipients = self.get_mail_recipients()
            if not recipients:
                raise ValueError("Mail alıcısı bulunamadı.")

            formatted_date = localtime(timezone.now()).strftime("%d.%m.%Y %H:%M")
            subject = f"Top 20 Müşteri Riski – {formatted_date}"

            context["report_date"] = formatted_date
            context.setdefault("report_title", "Top 20 Müşteri Bakiye Özeti")

            template_html = 'mailservice/report_orchestrator/totalrisk/top_balance_report_email.html'

            mail_log = MailLog.objects.create(
                mail_type='Rapor',
                subject=subject,
                recipients=recipients,
                sender=settings.DEFAULT_FROM_EMAIL,
                created_by=None,
                created_by_email=None,
                has_attachments=False,
                related_object_type='customer_balance_top20',
                related_object_id=None,
                status='PENDING'
            )

            html_content = render_to_string(template_html, context)

            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients
            )
            email.content_subtype = "html"

            mail_log.status = 'SENDING'
            mail_log.save()

            email.send(fail_silently=False)

            mail_log.status = 'SENT'
            mail_log.sent_at = timezone.now()
            mail_log.save()
            return True

        except Exception as e:
            if mail_log:
                mail_log.status = 'FAILED'
                mail_log.error_message = str(e)
                mail_log.save()
            print(f"[MAIL ERROR] Top 20 müşteri bakiyesi maili gönderilemedi: {str(e)}")
            return False
