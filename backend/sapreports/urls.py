# backend/sapreports/urls.py
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.conf import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ---- Yalnızca şema görünümleri için özel auth/perm -----------------
schema_view = SpectacularAPIView.as_view(
    authentication_classes=[SessionAuthentication],
    permission_classes=[IsAdminUser],
)

swagger_view = SpectacularSwaggerView.as_view(
    url_name="api-schema",
    authentication_classes=[SessionAuthentication],
    permission_classes=[IsAdminUser],
)

redoc_view = SpectacularRedocView.as_view(
    url_name="api-schema",
    authentication_classes=[SessionAuthentication],
    permission_classes=[IsAdminUser],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # hana db apiler
    path('api/v2/activities/', include('activities.api.urls')),
    path('api/v2/authcentral/', include('authcentral.api.urls')),
    path('api/v2/bomcostmanager/', include('bomcostmanager.api.urls')),
    path('api/v2/crmblog/', include('crmblog.api.urls')),
    path('api/v2/customercollection/', include('customercollection.api.urls')),
    path('api/v2/customersales/', include('customersales.api.urls')),
    path('api/v2/deliverydocsum/', include('deliverydocsum.api.urls')),
    path('api/v2/deliverydocsumv2/', include('deliverydocsumv2.api.urls')),
    #path('api/v2/docarchive/', include('docarchive.api.urls')),
    path('api/v2/docarchivev2/', include('docarchivev2.api.urls')),
    path('api/v2/dpap/', include('dpap.api.urls')),
    path('api/v2/eduvideo/', include('eduvideo.api.urls')),
    path('api/v2/filesharehub/', include('filesharehub.api.urls')),
    path('api/v2/filesharehub-v2/', include('filesharehub_v2.api.urls')),
    path('api/v2/girsbergerordropqt/', include('girsbergerordropqt.api.urls')),
    path('api/v2/hanadbcon/', include('hanadbcon.api.urls')),
    path('api/v2/hanadbintegration/', include('hanadbintegration.api.urls')),
    path('api/v2/logo_supplier_receivables_aging/', include('logo_supplier_receivables_aging.api.urls')), 
    path('api/v2/logocustomerbalance/', include('logocustomerbalance.api.urls')), 
    path('api/v2/logocustomercollection/', include('logocustomercollection.api.urls')),
    path('api/v2/logodbcon/', include('logodbcon.api.urls')),
    path('api/v2/logosupplierbalance/', include('logosupplierbalance.api.urls')), 
    path('api/v2/mailservice/', include('mailservice.api.urls')),
    path('api/v2/newcustomerform/', include('newcustomerform.api.urls')),
    path('api/v2/openorderdocsum/', include('openorderdocsum.api.urls')),
    path('api/v2/orderarchive/', include('orderarchive.urls.order_archive_urls')),
    path('api/v2/procure_compare/', include('procure_compare.urls')),
    path('api/v2/productconfig/', include('productconfig.api.urls')),
    path('api/v2/productconfigv2/', include('productconfigv2.api.urls')),
    path('api/v2/productconfig_simulator/', include('productconfig_simulator.api.urls')),
    path('api/v2/productgroupdeliverysum/', include('productgroupdeliverysum.api.urls')),
   # path('api/v2/productpicture/', include('productpicture.api.urls')),
    path('api/v2/rawmaterialwarehousestock/', include('rawmaterialwarehousestock.api.urls')),
    path('api/v2/report_orchestrator/', include('report_orchestrator.api.urls')),
    path('api/v2/salesbudget/', include('salesbudget.api.urls')),
    path('api/v2/salesbudgeteur/', include('salesbudgeteur.api.urls')),
    path('api/v2/salesbudgetv2/', include('salesbudgetv2.api.urls')),
    path('api/v2/salesinvoicesum/', include('salesinvoicesum.api.urls')),
    path('api/v2/salesofferdocsum/', include('salesofferdocsum.api.urls')),
    path('api/v2/salesorder/', include('salesorder.api.urls')),
    path('api/v2/salesorderdetail/', include('salesorderdetail.api.urls')),
    path('api/v2/salesorderdocsum/', include('salesorderdocsum.api.urls')),
    path('api/v2/shipweekplanner/', include('shipweekplanner.api.urls')),
    path('api/v2/stockcardintegration/', include('stockcardintegration.api.urls')),
    path('api/v2/supplierpayment/', include('supplierpayment.api.urls')),
    path('api/v2/systemnotebook/', include('systemnotebook.api.urls')),
    path('api/v2/taskorchestrator/', include('taskorchestrator.api.urls')),
    path('api/v2/totalrisk/', include('totalrisk.api.urls')),

    path('api/v2/dynamicreport/', include('dynamicreport.api.urls')), # dynamicreport dinamik sql sorgular

    # Tuna Ins api
    path('api/v2/tunainstotalrisk/', include('tunainstotalrisk.api.urls')),
    path('api/v2/tunainssupplierpayment/', include('tunainssupplierpayment.api.urls')),
    path('api/v2/tunainssupplieradvancebalance/', include('tunainssupplieradvancebalance.api.urls')),

    # drf_spectacular URL'leri
    path("api/schema/", schema_view, name="api-schema"),
    path("api/schema/swagger-ui/", swagger_view, name="swagger-ui"),
    path("api/schema/redoc/", redoc_view, name="redoc"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
