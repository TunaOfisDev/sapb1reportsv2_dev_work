# path: backend/formforgeapi/api/urls.py

from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, 
    FormViewSet, 
    FormFieldViewSet, 
    FormSubmissionViewSet, 
    SubmissionValueViewSet
)

router = DefaultRouter()

# Frontend API istemcisiyle uyumlu olması için alt çizgi (_) kullanıyoruz.
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'form_fields', FormFieldViewSet, basename='form-field')
router.register(r'form_submissions', FormSubmissionViewSet, basename='submission')
router.register(r'submission_values', SubmissionValueViewSet, basename='submission-value')

urlpatterns = router.urls