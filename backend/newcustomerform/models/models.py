# backend/newcustomerform/models/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .base import TimeStampedModel

def validate_file_size(file):
    max_size_mb = 1
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Dosya boyutu {max_size_mb}MB'dan fazla olamaz.")

class NewCustomerForm(TimeStampedModel):
    firma_unvani = models.CharField(max_length=255, verbose_name="Firma Ünvanı")
    vergi_kimlik_numarasi = models.CharField(max_length=50, verbose_name="Vergi Kimlik Numarası / T.C. Kimlik No")
    vergi_dairesi = models.CharField(max_length=255, verbose_name="Vergi Dairesi")
    firma_adresi = models.TextField(verbose_name="Firma Adresi")
    telefon_numarasi = models.CharField(max_length=20, verbose_name="Telefon Numarası")
    email = models.EmailField(verbose_name="E-posta Adresi")
    muhasebe_irtibat_telefon = models.CharField(max_length=20, verbose_name="Muhasebe İrtibat Telefonu")
    muhasebe_irtibat_email = models.EmailField(verbose_name="Muhasebe İrtibat E-posta")
    odeme_sartlari = models.TextField(verbose_name="Ödeme Şartları ve Vadeleri")
    iskonto_anlasmasi = models.TextField(verbose_name="İskonto veya Özel Fiyat Anlaşması", blank=True, null=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Oluşturan Kullanıcı",
        related_name="customer_forms"
    )


    vergi_levhasi = models.FileField(
        upload_to='new_customer_attachments/', 
        validators=[validate_file_size], 
        verbose_name="Vergi Levhası",
        blank=True,  # Form validation için opsiyonel
        null=True    # Database için opsiyonel
    )
    faaliyet_belgesi = models.FileField(
        upload_to='new_customer_attachments/', 
        validators=[validate_file_size], 
        verbose_name="Faaliyet Belgesi",
        blank=True, 
        null=True
    )
    ticaret_sicil = models.FileField(
        upload_to='new_customer_attachments/', 
        validators=[validate_file_size], 
        verbose_name="Ticaret Sicil Gazetesi",
        blank=True, 
        null=True
    )
    imza_sirkuleri = models.FileField(
        upload_to='new_customer_attachments/', 
        validators=[validate_file_size], 
        verbose_name="İmza Sirküleri",
        blank=True, 
        null=True
    )
    banka_iban = models.FileField(
        upload_to='new_customer_attachments/', 
        validators=[validate_file_size], 
        verbose_name="Banka IBAN Bilgileri",
        blank=True, 
        null=True
    )
    


    class Meta:
        verbose_name = "Yeni Müşteri Formu"
        verbose_name_plural = "Yeni Müşteri Formları"

    def __str__(self):
        return self.firma_unvani


class AuthorizedPerson(TimeStampedModel):
    new_customer_form = models.ForeignKey(
        NewCustomerForm, 
        on_delete=models.CASCADE, 
        related_name="yetkili_kisiler", 
        verbose_name="Yeni Müşteri Formu",
        blank=True,  #  Opsiyonel olması için eklendi
        null=True     #   Opsiyonel olması için eklendi
    )
    ad_soyad = models.CharField(max_length=255, verbose_name="Yetkili Kişi Adı Soyadı", blank=True, null=True)
    telefon = models.CharField(max_length=20, verbose_name="Yetkili Telefon", blank=True, null=True)
    email = models.EmailField(verbose_name="Yetkili E-posta", blank=True, null=True)

    class Meta:
        verbose_name = "Yetkili Kişi"
        verbose_name_plural = "Yetkili Kişiler"

    def __str__(self):
        return self.ad_soyad if self.ad_soyad else "Yetkili Kişi (Bilinmiyor)"