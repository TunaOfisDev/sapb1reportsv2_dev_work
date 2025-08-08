# path: backend/formforgeapi/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, 
    FormViewSet, 
    FormFieldViewSet, 
    FormSubmissionViewSet, 
    SubmissionValueViewSet,
    UserViewSet # UserViewSet import edildi
)

router = DefaultRouter()

router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'form_fields', FormFieldViewSet, basename='form-field')
router.register(r'form_submissions', FormSubmissionViewSet, basename='formsubmission')
router.register(r'submission_values', SubmissionValueViewSet, basename='submission-value')
router.register(r'users', UserViewSet, basename='user') # UserViewSet router'a eklendi

urlpatterns = [
    path('', include(router.urls)),
]