# backend/stockcardintegration/services/mail/send_stockcard_summary_email.py

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

ITEMS_GROUP_LABELS = {
    105: "MAMUL",
    112: "GİRSBERGER",
    103: "TİCARİ"
}

def get_stockcard_recipients(initiated_user_email):
    """
    'Stok_Kart_Entegrasyon_Email' departman üyeleri + işlemi yapan kullanıcıyı döner.
    """
    User = get_user_model()
    department_users = User.objects.filter(departments__name="Stok_Kart_Entegrasyon_Email")
    emails = list(department_users.values_list("email", flat=True))
    if initiated_user_email not in emails:
        emails.append(initiated_user_email)
    return list(set(emails))

def send_stockcard_summary_email(to_email, created_cards=None, updated_cards=None, error_logs=None, initiated_by=None):
    """
    Tekil veya çoklu SAP stok kartı işlemleri için özet mail gönderir.
    """
    created_cards = created_cards or []
    updated_cards = updated_cards or []
    error_logs = error_logs or []

    all_success_cards = created_cards + updated_cards
    success_count = len(all_success_cards)
    fail_count = len(error_logs)

    if created_cards and not updated_cards:
        action_type = "Yeni Kart"
    elif updated_cards and not created_cards:
        action_type = "Güncelleme"
    else:
        action_type = "Karışık"

    subject = "[SAP Özet] Stok Kartı İşlem Raporu"

    success_lines = "\n".join([
        f"- {item.item_code} | {item.item_name} | {item.price} {item.currency} | Grup: {item.items_group_code}-{ITEMS_GROUP_LABELS.get(item.items_group_code, 'BİLİNMİYOR')}"
        for item in all_success_cards
    ]) if success_count else "-"

    fail_lines = "\n".join([
        f"- {e.get('item_code', 'Bilinmiyor')} => {e.get('error', 'Hata nedeni bilinmiyor')}"
        for e in error_logs
    ]) if fail_count else "-"

    message = (
        "SAP HANA - Stok Kartı Toplu İşlem Özeti\n"
        "------------------------------------------------------------\n"
        f"👤 İşlemi Yapan: {initiated_by or to_email}\n"
        f"📌 İşlem Tipi: {action_type}\n\n"
        f"✅ Başarıyla İşlenen Kartlar: {success_count} adet\n\n"
        f"{success_lines}\n\n"
        f"❌ Hatalı Girişler: {fail_count} adet\n\n"
        f"{fail_lines}\n\n"
        "------------------------------------------------------------\n"
        "Bu e-posta SAP stok kartı entegrasyon modülü tarafından otomatik olarak oluşturulmuştur.\n"
    )

    recipients = get_stockcard_recipients(to_email)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False
    )