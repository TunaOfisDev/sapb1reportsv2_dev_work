# path: backend/formforgeapi/services/formforgeapi_service.py
import json
import re
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator, EmailValidator
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from ..utils.formfields import FieldTypes

# ==============================================================================
# LİSTELEME (GET) SERVİSLERİ
# ==============================================================================

def get_department_list():
    return Department.objects.all()

def get_form_list():
    return Form.objects.select_related('department', 'created_by').prefetch_related('fields')

def get_formfield_list():
    return FormField.objects.select_related('form').all()

def get_user_list():
    """
    CustomUser modeline göre güncellendi.
    Frontend'deki 'userpicker' alanı için departman ve pozisyon bilgileriyle zenginleştirilmiş,
    aktif kullanıcıların tam QuerySet'ini döndürür.
    prefetch_related ile veritabanı sorguları optimize edilmiştir.
    """
    User = get_user_model()
    return User.objects.filter(is_active=True).prefetch_related(
        'departments', 
        'positions'
    ).order_by('email')

# ==============================================================================
# VERİ İŞLEME (POST, PUT) SERVİSLERİ
# ==============================================================================

def _validate_and_process_value(field, value):
    """
    Tek bir alanın değerini, alan tipine göre doğrulayan ve işleyen yardımcı fonksiyon.
    Hata durumunda DRF ValidationError fırlatır.
    """
    field_type = field.field_type
    
    if not field.is_required and (value is None or value == ''):
        return ''

    if field.is_required and (value is None or value == ''):
        raise DRFValidationError(f"'{field.label}' alanı zorunludur.")

    try:
        if field_type in [FieldTypes.NUMBER, FieldTypes.CURRENCY, FieldTypes.PERCENTAGE]:
            return str(float(value))
        
        elif field_type == FieldTypes.EMAIL:
            EmailValidator()(value)
            return value

        elif field_type == FieldTypes.URL:
            URLValidator()(value)
            return value

        elif field_type == FieldTypes.USER_PICKER:
            User = get_user_model()
            if not User.objects.filter(pk=value).exists():
                raise DRFValidationError(f"Geçersiz kullanıcı ID'si: {value}")
            return str(value)

        elif field_type == FieldTypes.DEPARTMENT_PICKER:
            # Not: Bu, formforgeapi'nin kendi Department modelini kontrol eder.
            # authcentral'ın Department modelini de kontrol etmek gerekebilir.
            if not Department.objects.filter(pk=value).exists():
                raise DRFValidationError(f"Geçersiz departman ID'si: {value}")
            return str(value)

        elif field_type == FieldTypes.MULTI_SELECT:
            if not isinstance(value, list):
                raise DRFValidationError("Çoklu seçim alanı bir liste olmalıdır.")
            return json.dumps(value, ensure_ascii=False)
            
        else:
            return str(value)

    except (ValueError, TypeError):
        raise DRFValidationError(f"'{field.label}' alanı için geçersiz değer: {value}")
    except DjangoValidationError as e:
        raise DRFValidationError(f"'{field.label}' alanında doğrulama hatası: {e.message}")


@transaction.atomic
def create_submission(form_id, values_data, user):
    """
    Gelen veriyi doğrulayarak yeni bir form gönderimi oluşturur.
    """
    try:
        form_instance = Form.objects.prefetch_related('fields').get(pk=form_id)
    except Form.DoesNotExist:
        raise DRFValidationError("Form bulunamadı.")

    fields_map = {field.id: field for field in form_instance.fields.all()}
    
    new_submission = FormSubmission.objects.create(form=form_instance, created_by=user)
    
    for value_data in values_data:
        field_id = value_data.get('form_field')
        value = value_data.get('value')
        
        field_instance = fields_map.get(field_id)
        if not field_instance:
            continue
            
        processed_value = _validate_and_process_value(field_instance, value)
        
        SubmissionValue.objects.create(
            submission=new_submission,
            form_field=field_instance,
            value=processed_value
        )
        
    return new_submission


@transaction.atomic
def update_submission_and_create_new_version(original_submission_id, values_data, user):
    """
    Mevcut bir gönderiyi günceller. Eskisini pasif hale getirir ve doğrulanmış veri ile yeni bir versiyon oluşturur.
    """
    try:
        original_submission = FormSubmission.objects.select_related('form__department').prefetch_related('form__fields').get(pk=original_submission_id)
    except FormSubmission.DoesNotExist:
        raise DRFValidationError("Güncellenecek gönderi bulunamadı.")

    root_submission = original_submission.parent_submission or original_submission
    
    FormSubmission.objects.filter(parent_submission=root_submission, is_active=True).update(is_active=False)
    if not original_submission.parent_submission:
        original_submission.is_active = False
        original_submission.save()

    new_version_number = root_submission.versions.count() + (1 if original_submission.parent_submission else 2)
    
    new_submission = FormSubmission.objects.create(
        form=original_submission.form,
        created_by=user,
        parent_submission=root_submission,
        version=new_version_number,
        is_active=True
    )

    fields_map = {field.id: field for field in original_submission.form.fields.all()}

    for value_data in values_data:
        field_id = value_data.get('form_field')
        value = value_data.get('value')
        
        field_instance = fields_map.get(field_id)
        if not field_instance:
            continue
            
        processed_value = _validate_and_process_value(field_instance, value)
        
        SubmissionValue.objects.create(
            submission=new_submission,
            form_field=field_instance,
            value=processed_value
        )
        
    return new_submission


@transaction.atomic
def update_formfield_order(data): # <<<--- FONKSİYON ADININ BU OLDUĞUNDAN EMİN OL
    """
    Form alanlarının sırasını toplu olarak günceller.
    Gelen veri: [{'id': 1, 'order': 0}, {'id': 2, 'order': 1}, ...]
    """
    updated_instances = []
    # Gelen verinin bir liste olduğundan emin olalım
    if not isinstance(data, list):
        raise DRFValidationError("Beklenen veri formatı liste değil.")

    for item in data:
        # Her bir item'ın 'id' ve 'order' içerdiğinden emin olalım
        if 'id' not in item or 'order' not in item:
            continue # veya hata fırlat
        
        # Sadece `order` alanını güncellemek için boş bir FormField instance'ı oluşturuyoruz.
        instance = FormField(id=item['id'], order=item['order'])
        updated_instances.append(instance)

    try:
        # bulk_update ile tek bir veritabanı sorgusunda tüm sıralamayı güncelle
        FormField.objects.bulk_update(updated_instances, ['order'])
        return Response({"message": "Sıralama başarıyla güncellendi."}, status=status.HTTP_200_OK)
    except Exception as e:
        # Hata durumunda daha anlamlı bir mesaj döndür
        raise DRFValidationError(f"Sıralama güncellenirken bir veritabanı hatası oluştu: {str(e)}")


@transaction.atomic
def create_new_form_version(original_form_id, user):
    original_form = Form.objects.get(pk=original_form_id)
    base_title = re.sub(r'_V\d+$', '', original_form.title)
    latest_version = Form.objects.filter(title__startswith=base_title).count()
    new_version_number = latest_version + 1
    new_title = f"{base_title}_V{new_version_number}"
    original_fields = original_form.fields.all().prefetch_related('options')
    original_form.status = Form.FormStatus.ARCHIVED
    original_form.save()
    new_form = Form.objects.create(
        parent_form=original_form, version=new_version_number, title=new_title,
        description=original_form.description, department=original_form.department,
        created_by=user, status=Form.FormStatus.PUBLISHED
    )
    for field in original_fields:
        original_options = field.options.all()
        field.pk = None
        field.form = new_form
        field.save()
        for option in original_options:
            option.pk = None
            option.form_field = field
            option.save()
    return new_form