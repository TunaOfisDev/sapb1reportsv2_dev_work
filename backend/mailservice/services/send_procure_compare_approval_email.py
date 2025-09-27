# File: backend/mailservice/services/send_procure_compare_approval_email.py

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from authcentral.models import Department
from weasyprint import HTML
import json

from mailservice.models.models import MailLog
from procure_compare.models.approval import PurchaseApproval

User = get_user_model()


class ProcureCompareApprovalMailService:
    """Satınalma onayı için özelleştirilmiş mail servisi"""

    def get_mail_recipients(self, approval: PurchaseApproval):
        recipients = set()
        try:
            department = Department.objects.get(name="Satinalma")
            users = User.objects.filter(departments=department, is_active=True)
            recipients.update(users.values_list('email', flat=True))
            if approval.kullanici and approval.kullanici.email:
                recipients.add(approval.kullanici.email)
        except Department.DoesNotExist:
            if approval.kullanici and approval.kullanici.email:
                recipients.add(approval.kullanici.email)
        return list(recipients)

    def send_mail(self, approval: PurchaseApproval):
        try:
            recipients = self.get_mail_recipients(approval)
            if not recipients:
                raise ValueError("Mail alıcısı bulunamadı.")

            # ✅ Konu ve Şablon Seçimi - Action Bazlı
            if approval.action == 'onay_iptal':
                subject = f"Onay İptal Edildi - Belge No: {approval.belge_no}"
                template_html = 'mailservice/procure_compare_approval_cancel_email.html'
                template_pdf = 'mailservice/procure_compare_approval_cancel_email_pdf.html'
                filename_suffix = 'onay_iptal'

            elif approval.action == 'kismi_onay':
                subject = f"Kısmi Onay Verildi - Belge No: {approval.belge_no}"
                template_html = 'mailservice/procure_compare_partial_approval_email.html'
                template_pdf = 'mailservice/procure_compare_partial_approval_email_pdf.html'
                filename_suffix = 'kismi_onay'

            elif approval.action == 'red':
                subject = f"Satınalma Reddi - Belge No: {approval.belge_no}"
                template_html = 'mailservice/procure_compare_rejection_email.html'
                template_pdf = 'mailservice/procure_compare_rejection_email_pdf.html'
                filename_suffix = 'red'

            else:  # Normal Onay (action == 'onay')
                subject = f"Satınalma Onayı - Belge No: {approval.belge_no}"
                template_html = 'mailservice/procure_compare_approval_email.html'
                template_pdf = 'mailservice/procure_compare_approval_email_pdf.html'
                filename_suffix = 'onay'

            # ✅ Mail Log Kaydı
            mail_log = MailLog.objects.create(
                mail_type='Bildirim',
                subject=subject,
                recipients=recipients,
                sender=settings.DEFAULT_FROM_EMAIL,
                created_by=approval.kullanici,
                created_by_email=approval.kullanici.email,
                has_attachments=True,
                related_object_type='PurchaseApproval',
                related_object_id=approval.id,
                status='PENDING'
            )

            try:
                detay = approval.satir_detay_json or {}

                teklif_fiyatlari_raw = detay.get("teklif_fiyatlari", {})
                if isinstance(teklif_fiyatlari_raw, str):
                    try:
                        teklif_fiyatlari = json.loads(teklif_fiyatlari_raw)
                    except Exception:
                        teklif_fiyatlari = {}
                else:
                    teklif_fiyatlari = teklif_fiyatlari_raw

                referans_teklifler = detay.get("referans_teklifler", [])
                if isinstance(referans_teklifler, str):
                    try:
                        referans_teklifler = json.loads(referans_teklifler)
                    except Exception:
                        referans_teklifler = []

                context = {
                    "approval": approval,
                    "detay": detay,
                    "teklif_fiyatlari": teklif_fiyatlari,
                    "referans_teklifler": referans_teklifler,
                }

                # ✅ E-posta Gönderimi
                html_content = render_to_string(template_html, context)
                pdf_content = self._generate_pdf(context, template_pdf)

                email = EmailMessage(
                    subject=mail_log.subject,
                    body=html_content,
                    from_email=mail_log.sender,
                    to=recipients
                )
                email.content_subtype = "html"

                email.attach(
                    f'satinalma_{filename_suffix}_{approval.belge_no}.pdf',
                    pdf_content,
                    'application/pdf'
                )

                mail_log.status = 'SENDING'
                mail_log.save()

                email.send(fail_silently=False)

                mail_log.status = 'SENT'
                mail_log.sent_at = timezone.now()
                mail_log.save()
                return True

            except Exception as e:
                mail_log.status = 'FAILED'
                mail_log.error_message = str(e)
                mail_log.save()
                return False

        except Exception as e:
            print(f"[MAIL ERROR] Satınalma onay maili gönderilemedi: {str(e)}")
            return False

    def _generate_pdf(self, context, template_pdf):
        html_string = render_to_string(template_pdf, context)
        return HTML(string=html_string, base_url=".").write_pdf()
