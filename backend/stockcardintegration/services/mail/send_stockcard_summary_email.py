# backend/stockcardintegration/services/mail/send_stockcard_summary_email.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model

ITEMS_GROUP_LABELS = {105: "MAMUL", 112: "GİRSBERGER", 103: "TİCARİ"}


def get_stockcard_recipients(initiated_user_email):
    User = get_user_model()
    dept_users = User.objects.filter(departments__name="Stok_Kart_Entegrasyon_Email")
    emails = list(dept_users.values_list("email", flat=True))
    emails.append(initiated_user_email)
    return list(set(emails))


def send_stockcard_summary_email(
    to_email,
    created_cards=None,
    updated_cards=None,
    error_logs=None,
    initiated_by=None,
):
    created_cards = created_cards or []
    updated_cards = updated_cards or []
    error_logs = error_logs or []

    all_success_cards = created_cards + updated_cards

    # ✔️ Hazırlık – şablona geçecek zengin context
    context = {
        "initiated_by": initiated_by or to_email,
        "action_type_verbose": (
            "Yeni Kart" if created_cards and not updated_cards
            else "Güncelleme" if updated_cards and not created_cards
            else "Karışık"
        ),
        "success_cards": [
            {
                "item_code": c.item_code,
                "item_name": c.item_name,
                "price": c.price,
                "currency": c.currency,
                "items_group_code": c.items_group_code,
                "group_label": ITEMS_GROUP_LABELS.get(c.items_group_code, "BİLİNMİYOR"),
            }
            for c in all_success_cards
        ],
        "error_logs": error_logs,
    }
    context["success_count"] = len(context["success_cards"])
    context["fail_count"] = len(error_logs)

    subject = "[SAP Özet] Stok Kartı İşlem Raporu"

    # 🔸 Şablonları render et
    text_body = render_to_string("mail/stockcard_summary_email.txt", context)
    html_body = render_to_string("mail/stockcard_summary_email.html", context)

    # 🔸 Multipart e-posta
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=get_stockcard_recipients(to_email),
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
