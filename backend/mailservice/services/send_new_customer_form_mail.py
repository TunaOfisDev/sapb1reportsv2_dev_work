# backend/mailservice/services/send_new_customer_form_mail.py
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from authcentral.models import Department
from weasyprint import HTML
import zipfile
import io
import os
from ..models.models import MailLog
from newcustomerform.models.models import NewCustomerForm

User = get_user_model()

class NewCustomerFormMailService:
    """Yeni müşteri formu için özelleştirilmiş mail servisi"""
    
    def get_mail_recipients(self, created_by):
        """
        Mail alıcılarını belirle:
        - NewCustomerForm_Mail departmanına üye kullanıcılar
        - Formu oluşturan kullanıcı
        """
        recipients = set()  # Tekrar eden mailleri önlemek için set kullan
        
        try:
            # NewCustomerForm_Mail departmanını bul
            department = Department.objects.get(name="NewCustomerForm_Mail")
            # Bu departmana üye tüm kullanıcıların maillerini al
            department_users = User.objects.filter(departments=department, is_active=True)
            department_emails = department_users.values_list('email', flat=True)
            recipients.update(department_emails)
            # Formu oluşturan kullanıcının mailini ekle
            if created_by and created_by.email:
                recipients.add(created_by.email)
        except Department.DoesNotExist:
            # Departman bulunamazsa sadece formu oluşturan kullanıcıya gönder
            if created_by and created_by.email:
                recipients.add(created_by.email)
        
        return list(recipients)
    
    def send_mail(self, customer_form, created_by):
        """
        Mail gönderme ve loglama işlemlerini yapar.
        
        Args:
            customer_form: NewCustomerForm instance
            created_by: Formu oluşturan CustomUser instance
        
        Returns:
            bool: Mail gönderimi başarılı ise True, aksi halde False.
        """
        try:
            # Mail alıcılarını belirle
            recipients = self.get_mail_recipients(created_by)
            if not recipients:
                raise ValueError("Mail alıcısı bulunamadı")
            
            # Mail log kaydını oluştur
            mail_log = MailLog.objects.create(
                mail_type='NEW_CUSTOMER_FORM',
                subject=f"Yeni Müşteri Formu - {customer_form.firma_unvani}",
                recipients=recipients,
                sender=settings.DEFAULT_FROM_EMAIL,
                created_by=created_by,
                created_by_email=created_by.email if created_by else None,
                has_attachments=True,
                related_object_type='NewCustomerForm',
                related_object_id=customer_form.id,
                status='PENDING'
            )
            
            try:
                # PDF ve ZIP dosyalarını oluştur
                pdf_content = self._generate_pdf(customer_form)
                zip_content = self._create_attachments_zip(customer_form)
                
                # Mail içeriğini hazırla
                context = {
                    'customer_form': customer_form,
                    'created_by': created_by,
                }
                message = render_to_string('mailservice/new_customer_form_email.html', context)
                
                # Email nesnesini oluştur
                email = EmailMessage(
                    subject=mail_log.subject,
                    body=message,
                    from_email=mail_log.sender,
                    to=recipients
                )
                
                # Önemli: Mail içeriğinin HTML olarak gönderilmesini sağla
                email.content_subtype = "html"
                
                email.attach(
                    f'musteri_formu_{customer_form.id}.pdf',
                    pdf_content,
                    'application/pdf'
                )
                
                email.attach(
                    f'ekler_{customer_form.id}.zip',
                    zip_content,
                    'application/zip'
                )
                
                # Gönderim öncesi log durumunu güncelle
                mail_log.status = 'SENDING'
                mail_log.save()
                
                # Maili gönder
                email.send(fail_silently=False)
                
                # Gönderim sonrası logu güncelle
                mail_log.status = 'SENT'
                mail_log.sent_at = timezone.now()
                mail_log.save()
                return True
            except Exception as e:
                # Mail gönderimi sırasında hata oluşursa logu güncelle
                mail_log.status = 'FAILED'
                mail_log.error_message = str(e)
                mail_log.save()
                return False
        except Exception as e:
            print(f"Mail servisi hatası: {str(e)}")
            return False
    
    def resend_mail(self, form_id, created_by):
        """
        Formu yeniden gönder.
        Args:
            form_id: Form ID
            created_by: Kullanıcı
        Returns:
            bool: Başarılı/Başarısız
        """
        try:
            customer_form = NewCustomerForm.objects.get(id=form_id)
            return self.send_mail(customer_form=customer_form, created_by=created_by)
        except NewCustomerForm.DoesNotExist:
            print(f"Form bulunamadı: {form_id}")
            return False
        except Exception as e:
            print(f"Mail yeniden gönderme hatası: {str(e)}")
            return False
        

                
    def _generate_pdf(self, customer_form):
        """PDF dosyası oluştur"""
        template = 'mailservice/new_customer_form_pdf.html'
        context = {
            'form': customer_form,
            'title': 'Yeni Müşteri Formu'
        }
        
        html_string = render_to_string(template, context)
        pdf_file = HTML(string=html_string, base_url=".").write_pdf()
        return pdf_file
        
    def _create_attachments_zip(self, customer_form):
        """Form eklerini ZIP dosyası olarak hazırla"""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            zip_buffer,
            'w',
            zipfile.ZIP_DEFLATED,
            compresslevel=6
        ) as zip_file:
            # Ekleri ZIP'e ekle
            attachments = [
                'vergi_levhasi',
                'faaliyet_belgesi',
                'ticaret_sicil',
                'imza_sirkuleri',
                'banka_iban'
            ]
            for attachment in attachments:
                file_field = getattr(customer_form, attachment)
                if file_field:
                    file_path = file_field.path
                    arcname = os.path.basename(file_path)
                    zip_file.write(file_path, arcname)
        return zip_buffer.getvalue()
