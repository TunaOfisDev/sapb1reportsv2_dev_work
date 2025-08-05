# path: backend/formforgeapi/api/urls.py
from rest_framework import routers
from .views import DepartmentViewSet, FormViewSet, FormFieldViewSet, FormSubmissionViewSet

router = routers.DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'forms', FormViewSet)
router.register(r'form-fields', FormFieldViewSet)
router.register(r'form-submissions', FormSubmissionViewSet)

urlpatterns = router.urls

