# backend/mailservice/services/stockcardintegration/update_stock_card_on_hanadb.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from stockcardintegration.models.models import StockCard

User = get_user_model()

def get_recipients(stock_card_creator):
    department_users = User.objects.filter(departments__name="Stok_Kart_Entegre_Mail")
    emails = list(department_users.values_list('email', flat=True))
    if stock_card_creator.email not in emails:
        emails.append(stock_card_creator.email)
    return emails


def send_stockcard_update_success_email(stock_card: StockCard, updated_by):
    context = {
        "stock_card": stock_card,
        "updated_by": updated_by
    }

    html_content = render_to_string("mailservice/stockcardintegration/update_success_email.html", context)
    subject = f"[STOK KARTI GÜNCELLENDİ] {stock_card.item_code} - {stock_card.item_name}"

    recipients = get_recipients(updated_by)

    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        html_message=html_content
    )


def send_stockcard_update_failure_email(stock_card: StockCard, updated_by, error_message: str):
    context = {
        "stock_card": stock_card,
        "updated_by": updated_by,
        "error_message": error_message
    }

    html_content = render_to_string("mailservice/stockcardintegration/update_failure_email.html", context)
    subject = f"[STOK KARTI GÜNCELLEME HATASI] {stock_card.item_code} güncellenemedi"

    recipients = get_recipients(updated_by)

    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        html_message=html_content
    )
