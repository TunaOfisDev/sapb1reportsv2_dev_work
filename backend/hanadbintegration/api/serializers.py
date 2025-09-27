# backend/hanadbintegration/api/serializers.py

from rest_framework import serializers
from ..models.models import HANADBIntegration

class HANADBIntegrationSerializer(serializers.ModelSerializer):
    """
    HANA DB Entegrasyonu için Serializer.
    - Yalnızca "Create", "Read" ve "Update" işlemlerini destekler.
    - "Delete" işlemi devre dışı bırakılmıştır.
    """

    class Meta:
        model = HANADBIntegration
        fields = (
            "id",
            "integration_name",
            "integration_type",
            "external_api_url",
            "hana_status",
            "last_synced_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "hana_status", "last_synced_at", "created_at", "updated_at")

    def validate_external_api_url(self, value):
        """
        API URL doğrulaması.
        - HTTP veya HTTPS içermelidir.
        - Boş olamaz.
        """
        if not value.startswith("http://") and not value.startswith("https://"):
            raise serializers.ValidationError("Geçersiz API URL! HTTP veya HTTPS ile başlamalıdır.")
        return value

    def delete(self, instance):
        """
        Silme işlemi devre dışı bırakıldı.
        """
        raise serializers.ValidationError("Bu veri silinemez! HANA DB üzerinde DELETE işlemi yasaktır.")
