# path: backend/formforgeapi/models/formforgeapi.py
from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name="Departman Adı")

    def __str__(self):
        return self.name

class Form(models.Model):
    title = models.CharField(max_length=255, verbose_name="Form Başlığı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Departman")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Oluşturan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    def __str__(self):
        return self.title

class FormField(models.Model):
    class FieldType(models.TextChoices):
        TEXT = 'text', 'Metin'
        NUMBER = 'number', 'Sayı'
        DATE = 'date', 'Tarih'
        TEXTAREA = 'textarea', 'Uzun Metin'
        SELECT = 'select', 'Seçim'
        CHECKBOX = 'checkbox', 'Onay Kutusu'
        RADIO = 'radio', 'Radyo Düğmesi'


    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='fields', verbose_name="Form")
    label = models.CharField(max_length=255, verbose_name="Etiket")
    field_type = models.CharField(max_length=20, choices=FieldType.choices, verbose_name="Alan Tipi")
    is_required = models.BooleanField(default=False, verbose_name="Zorunlu")
    is_master = models.BooleanField(default=False, verbose_name="Ana Listede Göster")
    order = models.IntegerField(default=0, verbose_name="Sıralama")

    def __str__(self):
        return self.label

class FormSubmission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="Form")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Oluşturan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    def __str__(self):
        return f"{self.form.title} - {self.created_at}"

class SubmissionValue(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='values', verbose_name="Form Gönderimi")
    form_field = models.ForeignKey(FormField, on_delete=models.CASCADE, verbose_name="Form Alanı")
    value = models.TextField(verbose_name="Değer")

    def __str__(self):
        return self.value

