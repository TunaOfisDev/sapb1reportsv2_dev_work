# backend/dpap/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models.models import API, APIAccessPermission, APIAuditLog
from .resources import APIResource, APIAccessPermissionResource, APIAuditLogResource


@admin.register(API)
class APIAdmin(ImportExportModelAdmin):
    """
    API modelini admin panelinde yönetmek için yapılandırma.
    Import/Export özelliklerini ekledik.
    """
    resource_class = APIResource
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(APIAccessPermission)
class APIAccessPermissionAdmin(ImportExportModelAdmin):
    """
    APIAccessPermission modelini admin panelinde yönetmek için yapılandırma.
    Import/Export özelliklerini ekledik.
    """
    resource_class = APIAccessPermissionResource
    list_display = ('api', 'can_create', 'can_read', 'can_update', 'can_delete', 'created_at', 'updated_at')
    list_filter = ('can_create', 'can_read', 'can_update', 'can_delete', 'departments', 'positions')
    search_fields = ('api__name',)
    ordering = ('api__name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(APIAuditLog)
class APIAuditLogAdmin(ImportExportModelAdmin):
    """
    APIAuditLog modelini admin panelinde yönetmek için yapılandırma.
    Import/Export özelliklerini ekledik.
    """
    resource_class = APIAuditLogResource
    list_display = ('user', 'api', 'accessed_at', 'success')
    list_filter = ('success', 'accessed_at')
    search_fields = ('user__email', 'api__name')
    ordering = ('-accessed_at',)
    readonly_fields = ('user', 'api', 'accessed_at', 'success')

    def has_add_permission(self, request):
        # API loglarına manuel ekleme izni vermiyoruz, sadece görüntüleme yapılabilir.
        return False
