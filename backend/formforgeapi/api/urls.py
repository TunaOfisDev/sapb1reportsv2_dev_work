# path: backend/formforgeapi/api/urls.py

from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, FormViewSet, FormFieldViewSet, FormSubmissionViewSet, SubmissionValueViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'form_fields', FormFieldViewSet, basename='formfield')
router.register(r'form_submissions', FormSubmissionViewSet, basename='formsubmission')
router.register(r'submission_values', SubmissionValueViewSet, basename='submissionvalue')

urlpatterns = router.urls

