# path: backend/formforgeapi/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, 
    FormViewSet, 
    FormFieldViewSet, 
    FormSubmissionViewSet, 
    SubmissionValueViewSet,
    UserViewSet,
    UpdateFormFieldOrderView 
)

router = DefaultRouter()

# ViewSet'ler router tarafından yönetilmeye devam ediyor
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'form_fields', FormFieldViewSet, basename='form-field')
router.register(r'form_submissions', FormSubmissionViewSet, basename='formsubmission')
router.register(r'submission_values', SubmissionValueViewSet, basename='submission-value')
router.register(r'users', UserViewSet, basename='user')

# Ana URL listemiz
urlpatterns = [
    # GÜNCELLEME: Özel ve daha spesifik olan URL yolunu, genel router'dan ÖNCE tanımlıyoruz.
    path('form_fields/update_order/', UpdateFormFieldOrderView.as_view(), name='formfield-update-order'),
    
    # Router tarafından oluşturulan genel URL'ler en sona geliyor.
    path('', include(router.urls)),
]