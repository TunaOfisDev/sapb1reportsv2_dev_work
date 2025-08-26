# path: backend/nexuscore/api/serializers.py

from rest_framework import serializers
from ..models import DynamicDBConnection, VirtualTable, SharingStatus
from ..services import connection_manager

class DynamicDBConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicDBConnection
        fields = [
            'id', 'title', 'db_type', 'is_active', 'config_json',
            'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
        
        # ### DÜZELTME: `write_only` kuralını kaldırıyoruz. ###
        # Artık GET isteklerinde de bu alan (eğer istenirse) gelebilir.
        # Bu, "Düzenle" formunun dolu gelmesini sağlayacak.
        extra_kwargs = {
            'config_json': {'required': True}
        }

    def to_representation(self, instance):
        """
        GET isteklerinde `config_json` verisinin kendisi yerine
        sadece durumunu göstererek güvenliği sağlıyoruz.
        Bu metod, hassas verinin listelerde görünmesini engeller.
        """
        representation = super().to_representation(instance)
        # Detay görünümünde (formu doldurmak için) gerçek veriyi göstermemiz gerekebilir.
        # ViewSet'in context'ini kontrol ederek bunu yapabiliriz.
        # Şimdilik, her zaman maskeleyelim, ViewSet'te düzelteceğiz.
        if 'config_json' in representation:
            representation.pop('config_json')
        representation['config_status'] = "Yapılandırıldı (Güvenli)"
        return representation

    def create(self, validated_data):
        config = validated_data.get('config_json')
        db_type = validated_data.get('db_type')
        
        is_successful, message = connection_manager.test_connection_config(config, db_type)
        
        if not is_successful:
            raise serializers.ValidationError({"config_json": f"Bağlantı testi başarısız: {message}"})
        
        return super().create(validated_data)

# --- Sanal Tablo için Serializer ---
# (VirtualTableSerializer'da bir değişiklik yapmaya gerek yok, olduğu gibi kalabilir)
class VirtualTableSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    connection_display = serializers.StringRelatedField(source='connection', read_only=True)
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)
    connection_id = serializers.PrimaryKeyRelatedField(
        queryset=DynamicDBConnection.objects.filter(is_active=True), 
        source='connection', 
        write_only=True,
        label="Bağlantı ID"
    )
    class Meta:
        model = VirtualTable
        fields = [
            'id', 'title', 'connection_id', 'connection_display', 'sql_query', 
            'column_metadata', 'owner', 'sharing_status', 'sharing_status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'column_metadata', 'owner', 'created_at', 'updated_at']
        extra_kwargs = {
            'sql_query': {'required': True},
        }
    def validate_sql_query(self, value):
        query = value.strip().upper()
        if not query.startswith('SELECT'):
            raise serializers.ValidationError("Güvenlik nedeniyle yalnızca 'SELECT' sorgularına izin verilmektedir.")
        if ';' in value.strip():
            raise serializers.ValidationError("Güvenlik nedeniyle sorgu içinde çoklu komutlara izin verilmez (;).")
        return value