# backend/dpap/resources.py
from import_export import resources
from .models.models import API, APIAccessPermission, APIAuditLog

class APIResource(resources.ModelResource):
    class Meta:
        model = API
        fields = ('id', 'name', 'is_active', 'created_at', 'updated_at')


class APIAccessPermissionResource(resources.ModelResource):
    class Meta:
        model = APIAccessPermission
        fields = ('id', 'api__name', 'can_create', 'can_read', 'can_update', 'can_delete', 'created_at', 'updated_at')


class APIAuditLogResource(resources.ModelResource):
    class Meta:
        model = APIAuditLog
        fields = ('id', 'user__email', 'api__name', 'accessed_at', 'success', 'created_at', 'updated_at')
