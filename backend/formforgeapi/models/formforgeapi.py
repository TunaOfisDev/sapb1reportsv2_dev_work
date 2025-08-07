# path: backend/formforgeapi/models/formforgeapi.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Department(models.Model):
    name = models.CharField(_("Departman Adı"), max_length=255)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)

    def __str__(self):
        return self.name

class Form(models.Model):
    # YENİ: Form durumları için TextChoices ekliyoruz
    class FormStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Taslak')
        PUBLISHED = 'PUBLISHED', _('Dağıtımda')
        ARCHIVED = 'ARCHIVED', _('Arşivlenmiş')

    title = models.CharField(_("Form Başlığı"), max_length=255)
    description = models.TextField(_("Form Açıklaması"), blank=True)
    department = models.ForeignKey(Department, verbose_name=_("Departman"), on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Oluşturan Kullanıcı"), on_delete=models.CASCADE)
    
    # YENİ: Status alanı eklendi
    status = models.CharField(
        _("Durum"),
        max_length=10,
        choices=FormStatus.choices,
        default=FormStatus.PUBLISHED
    )

    # YENİ: Versiyonlama için alanlar
    parent_form = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='versions',
        verbose_name=_("Ana Form")
    )
    version = models.PositiveIntegerField(_("Versiyon"), default=1)
    
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)

    class Meta:
        ordering = ['-version'] # İsteğe bağlı: Versiyona göre sırala
        
    def __str__(self):
        return self.title


class FormField(models.Model):
    class FieldTypes(models.TextChoices):
        TEXT          = 'text',         _('Metin')
        NUMBER        = 'number',       _('Sayı')
        EMAIL         = 'email',        _('E-posta')
        TEXTAREA      = 'textarea',     _('Metin Alanı')
        SINGLE_SELECT = 'singleselect', _('Tekli Seçim')
        MULTI_SELECT  = 'multiselect',  _('Çoklu Seçim')
        CHECKBOX      = 'checkbox',     _('Onay Kutusu')
        RADIO         = 'radio',        _('Radyo Düğmesi')
        DATE          = 'date',         _('Tarih')

    form = models.ForeignKey(Form, verbose_name=_("Form"), on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(_("Etiket"), max_length=255)
    field_type = models.CharField(_("Alan Tipi"), max_length=20, choices=FieldTypes.choices)
    is_required = models.BooleanField(_("Zorunlu"), default=False)
    is_master = models.BooleanField(_("Ana Alan"), default=False)
    order = models.IntegerField(_("Sıralama"), default=0)
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)

    def __str__(self):
        return self.label

class FormSubmission(models.Model):
    form = models.ForeignKey(Form, verbose_name=_("Form"), on_delete=models.CASCADE, related_name='submissions')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Gönderen Kullanıcı"), on_delete=models.CASCADE)
    
    # --- YENİ ALANLAR: GÖNDERİM VERSİYONLAMA ---
    parent_submission = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='versions',
        verbose_name=_("Ana Gönderim")
    )
    version = models.PositiveIntegerField(_("Versiyon"), default=1)
    is_active = models.BooleanField(_("Aktif Versiyon"), default=True)
    # --- YENİ ALANLAR SONU ---
    
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)

    def __str__(self):
        user_info = self.created_by.email if self.created_by else 'Anonim Kullanıcı'
        return f"{self.form.title} - {user_info} (V{self.version})"




class SubmissionValue(models.Model):
    submission = models.ForeignKey(FormSubmission, verbose_name=_("Form Gönderimi"), on_delete=models.CASCADE, related_name='values')
    form_field = models.ForeignKey(FormField, verbose_name=_("Form Alanı"), on_delete=models.CASCADE)
    value = models.TextField(_("Değer"))
    created_at = models.DateTimeField(_("Oluşturulma Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncellenme Tarihi"), auto_now=True)

    def __str__(self):
        # Bu metot daha açıklayıcı hale getirildi.
        user_info = self.submission.created_by.email if self.submission.created_by else 'Anonim'
        return f"{self.submission.form.title} | {self.form_field.label}: {self.value} ({user_info})"


class FormFieldOption(models.Model):
    form_field = models.ForeignKey(
        FormField,
        verbose_name=_("Form Alanı"),
        related_name="options",
        on_delete=models.CASCADE,
    )
    label = models.CharField(_("Seçenek Metni"), max_length=255)
    order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.form_field.label} ⟶ {self.label}"