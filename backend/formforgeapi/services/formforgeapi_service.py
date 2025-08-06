# path: backend/formforgeapi/services/formforgeapi_service.py
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
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