# path: backend/formforgeapi/services/formforgeapi_service.py
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import json
import re

def get_department_list():
    return Department.objects.all()

def get_form_list():
    # YENİ: Sadece 'Dağıtımda' olan formları listeliyoruz.
    return Form.objects.filter(status=Form.FormStatus.PUBLISHED)\
        .select_related('department', 'created_by').prefetch_related('fields')


def get_formfield_list():
    return FormField.objects.select_related('form').all()


def get_formsubmission_list():
    return FormSubmission.objects.select_related('form', 'created_by').prefetch_related('values').all()


def get_submissionvalue_list():
    return SubmissionValue.objects.select_related('submission', 'form_field').all()


@transaction.atomic
def update_formfield_order(data):
    updated_instances = []
    for item in data:
        instance = FormField(id=item['id'], order=item['order'])
        updated_instances.append(instance)

    try:
        FormField.objects.bulk_update(updated_instances, ['order'])
        return Response({"message": "Sıralama başarıyla güncellendi."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
def create_new_form_version(original_form_id, user):
    original_form = Form.objects.get(pk=original_form_id)
    
    # 1. Yeni form için başlık ve versiyon numarasını belirle
    base_title = re.sub(r'_V\d+$', '', original_form.title)
    latest_version = Form.objects.filter(title__startswith=base_title).count()
    new_version_number = latest_version + 1
    new_title = f"{base_title}_V{new_version_number}"

    # 2. Orijinal formun alanlarını ve seçeneklerini topla
    original_fields = original_form.fields.all().prefetch_related('options')
    
    # 3. Orijinal formu Arşive al (isteğe bağlı)
    original_form.status = Form.FormStatus.ARCHIVED
    original_form.save()
    
    # 4. Formun bir kopyasını oluştur (yeni versiyon)
    new_form = Form.objects.create(
        parent_form=original_form,
        version=new_version_number,
        title=new_title,
        description=original_form.description,
        department=original_form.department,
        created_by=user,
        status=Form.FormStatus.PUBLISHED
    )
    
    # 5. Her bir alanı ve seçeneği kopyala
    for field in original_fields:
        original_options = field.options.all()
        field.pk = None # PK'yı None yaparak yeni bir obje oluşturmasını sağlıyoruz
        field.form = new_form
        field.save() # Yeni alanı kaydet
        
        # Seçenekleri kopyala
        for option in original_options:
            option.pk = None
            option.form_field = field
            option.save()
            
    return new_form


@transaction.atomic
def update_submission_and_create_new_version(original_submission_id, values_data, user):
    """
    Mevcut bir gönderiyi günceller. Aslında eskiyi pasif hale getirir ve yeni bir versiyon oluşturur.
    """
    # 1. Orijinal (güncellenmek istenen) gönderiyi bul.
    original_submission = FormSubmission.objects.select_related('parent_submission').get(pk=original_submission_id)
    
    # 2. Ana gönderimi belirle. Eğer bu ilk güncelleme ise, ana gönderi kendisidir.
    root_submission = original_submission.parent_submission or original_submission
    
    # 3. Bu ana gönderiye bağlı tüm versiyonları bul ve mevcut aktif olanı pasif yap.
    latest_version_qs = FormSubmission.objects.filter(parent_submission=root_submission, is_active=True)
    latest_version_qs.update(is_active=False)
    # Eğer bu ilk güncelleme ise, orijinal gönderiyi de pasif yap
    if not original_submission.parent_submission:
        original_submission.is_active = False
        original_submission.save()

    # 4. Yeni versiyon numarasını hesapla.
    new_version_number = root_submission.versions.count() + 2 # +1 kendisi, +1 yeni versiyon

    # 5. Yeni FormSubmission kaydını oluştur.
    new_submission = FormSubmission.objects.create(
        form=original_submission.form,
        created_by=user, # Güncellemeyi yapan kullanıcı yeni versiyonun sahibi olur
        parent_submission=root_submission,
        version=new_version_number,
        is_active=True
    )

    # 6. Yeni gönderim için yeni SubmissionValue'ları oluştur.
    field_types = {field.id: field.field_type for field in new_submission.form.fields.all()}
    for value_data in values_data:
        field_id = value_data.get('form_field')
        value = value_data.get('value')
        
        if field_types.get(field_id) == FormField.FieldTypes.MULTI_SELECT and isinstance(value, list):
            value_to_save = json.dumps(value, ensure_ascii=False)
        else:
            value_to_save = str(value) if value is not None else ''

        if field_id:
            SubmissionValue.objects.create(
                submission=new_submission,
                form_field_id=field_id,
                value=value_to_save
            )
            
    return new_submission