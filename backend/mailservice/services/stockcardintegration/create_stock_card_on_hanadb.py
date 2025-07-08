# backend/mailservice/services/stockcardintegration/create_stock_card_on_hanadb.py

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


def send_stockcard_create_success_email(stock_card: StockCard, created_by):
    context = {
        "stock_card": stock_card,
        "created_by": created_by
    }

    html_content = render_to_string("mailservice/stockcard/success_email.html", context)
    subject = f"[STOK KARTI OLUŞTURULDU] {stock_card.item_code} - {stock_card.item_name}"

    recipients = get_recipients(created_by)

    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        html_message=html_content
    )


def send_stockcard_create_failure_email(stock_card: StockCard, created_by, error_message: str):
    context = {
        "stock_card": stock_card,
        "created_by": created_by,
        "error_message": error_message
    }

    html_content = render_to_string("mailservice/stockcard/failure_email.html", context)
    subject = f"[STOK KARTI HATASI] {stock_card.item_code} gönderilemedi"

    recipients = get_recipients(created_by)

    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        html_message=html_content
    )
