# backend/dpap/serializers.py
from rest_framework import serializers
from .models.models import API, APIAccessPermission, APIAuditLog

class APISerializer(serializers.ModelSerializer):
    """
    API modelinin serileştiricisi.
    """
    class Meta:
        model = API
        fields = ['id', 'name', 'is_active']  # Sadece temel alanlar

class APIAccessPermissionSerializer(serializers.ModelSerializer):
    """
    APIAccessPermission modelinin serileştiricisi.
    """
    api = APISerializer(read_only=True)

    class Meta:
        model = APIAccessPermission
        fields = ['id', 'api', 'can_create', 'can_read', 'can_update', 'can_delete', 'departments', 'positions']

class APIAuditLogSerializer(serializers.ModelSerializer):
    """
    APIAuditLog modelinin serileştiricisi.
    """
    user = serializers.StringRelatedField(read_only=True)
    api = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = APIAuditLog
        fields = ['id', 'user', 'api', 'accessed_at', 'success', 'created_at', 'updated_at']

