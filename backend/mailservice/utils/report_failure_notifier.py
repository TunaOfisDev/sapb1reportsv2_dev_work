# backend/mailservice/utils/report_failure_notifier.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from authcentral.models import Department

def notify_report_failure(api_name: str, error_message: str, report_context: dict):
    try:
        department = Department.objects.get(name="Bilgi_Sistem")
        recipients = list(get_user_model().objects.filter(departments=department).values_list("email", flat=True))

        if not recipients:
            return False

        subject = f"[UYARI] {api_name} raporu başarısız oldu"
        body = render_to_string(
            'mailservice/report_orchestrator/failure_notification/report_failure_email.html',
            {
                "api_name": api_name,
                "error_message": error_message,
                "context": report_context,
            }
        )

        send_mail(
            subject=subject,
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=body,
            fail_silently=False
        )
        return True

    except Exception as e:
        print(f"[MAIL ERROR] Bilgi Sistem uyarı maili gönderilemedi: {str(e)}")
        return False
