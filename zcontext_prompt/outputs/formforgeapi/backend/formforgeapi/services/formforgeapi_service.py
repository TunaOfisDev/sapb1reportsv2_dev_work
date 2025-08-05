# path: backend/formforgeapi/services/formforgeapi_service.py
from ..models import Department, Form, FormField, FormSubmission, SubmissionValue
from typing import Iterable, Dict

def get_all_departments() -> Iterable[Department]:
    """Tüm departmanları döndürür."""
    return Department.objects.all()

def get_all_forms() -> Iterable[Form]:
    """Tüm formları döndürür."""
    return Form.objects.all()

def get_all_form_fields() -> Iterable[FormField]:
    """Tüm form alanlarını döndürür."""
    return FormField.objects.all()

def get_all_form_submissions() -> Iterable[FormSubmission]:
    """Tüm form gönderimlerini döndürür."""
    return FormSubmission.objects.all()

def save_submission(submission: FormSubmission, submitted_data: Dict) -> None:
    """Form gönderim değerlerini kaydeder."""
    form_fields = submission.form.fields.all()
    for field in form_fields:
        value = submitted_data.get(str(field.id))
        SubmissionValue.objects.create(submission=submission, form_field=field, value=value)

