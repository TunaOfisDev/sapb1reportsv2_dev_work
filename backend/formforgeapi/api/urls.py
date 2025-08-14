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

# 1. Router'ı Oluşturma
# DefaultRouter, ViewSet'ler için standart CRUD (list, create, retrieve, update, destroy)
# URL'lerini ve özel @action'ları otomatik olarak oluşturur.
router = DefaultRouter()

# 2. ViewSet'leri Router'a Kaydetme
# router.register('url-ön-eki', ViewSetSınıfı, basename='url-adı-için-temel')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'form-fields', FormFieldViewSet, basename='form-field')
router.register(r'submissions', FormSubmissionViewSet, basename='submission')
router.register(r'submission-values', SubmissionValueViewSet, basename='submission-value')
router.register(r'users', UserViewSet, basename='user')

# 3. Ana URL Listesini Tanımlama
urlpatterns = [
    # ÖZEL YOLLAR: Standart ViewSet mantığı dışındaki özel APIView'lar burada,
    # router'dan önce tanımlanmalıdır. Django URL'leri sırayla işler.
    path(
        'form-fields/update-order/',
        UpdateFormFieldOrderView.as_view(),
        name='formfield-update-order'
    ),

    # ROUTER YOLLARI: Router tarafından otomatik oluşturulan tüm URL'leri
    # projenin geri kalanına dahil et. Bu her zaman en sonda olmalıdır.
    path('', include(router.urls)),
]