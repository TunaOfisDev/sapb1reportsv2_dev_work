# path: /var/www/sapb1reportsv2/backend/nexuscore/api/serializers.py

from rest_framework import serializers
from ..models import DynamicDBConnection, VirtualTable, SharingStatus
from ..utils.db_helpers import test_database_connection

# --- Dinamik Veri Tabanı Bağlantısı için Serializer ---

class DynamicDBConnectionSerializer(serializers.ModelSerializer):
    """
    DynamicDBConnection modeli için veri doğrulama ve dönüştürme işlemleri.
    Modeldeki custom EncryptedJSONField ile tam uyumludur.
    GÜVENLİK ODAKLIDIR: Bağlantı bilgilerini asla GET isteklerinde ifşa etmez.
    """
    # Bu alanın görevi, gelen verinin geçerli bir JSON olup olmadığını kontrol etmektir.
    # Şifreleme işini, bu katman değil, model katmanındaki EncryptedJSONField yapar.
    # Bu yüzden buradaki tanımımız değişmedi.
    json_config = serializers.JSONField(write_only=True)

    class Meta:
        model = DynamicDBConnection
        fields = [
            'id', 'title', 'db_type', 'is_active', 
            'json_config', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        GET isteklerinde verinin nasıl gösterileceğini kontrol eder.
        Hassas `json_config` bilgisini maskeleyerek güvenliği sağlarız.
        Bu davranış, altta yatan şifreleme yönteminden bağımsızdır ve hala geçerlidir.
        """
        representation = super().to_representation(instance)
        representation['config_status'] = "Yapılandırıldı (Güvenli)"
        return representation

    def create(self, validated_data):
        """
        Yeni bir bağlantı oluşturulurken, kaydetmeden ÖNCE bağlantıyı test eder.
        Bu kritik doğrulama adımı, şifreleme yöntemimiz değişse de aynı kalır.
        """
        config = validated_data.get('json_config')
        
        is_successful, message = test_database_connection(config)
        
        if not is_successful:
            raise serializers.ValidationError({"json_config": f"Bağlantı testi başarısız: {message}"})
        
        return super().create(validated_data)


# --- Sanal Tablo için Serializer ---

class VirtualTableSerializer(serializers.ModelSerializer):
    """
    VirtualTable modeli için veri doğrulama ve dönüştürme.
    Modeldeki son değişiklikler (SharingStatus'un dışarı taşınması) ile tam uyumludur.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    
    connection_display = serializers.StringRelatedField(source='connection', read_only=True)
    connection_id = serializers.PrimaryKeyRelatedField(
        queryset=DynamicDBConnection.objects.all(), source='connection', write_only=True
    )
    
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)

    class Meta:
        model = VirtualTable
        fields = [
            'id', 'title', 'connection_id', 'connection_display', 'sql_query', 
            'column_metadata', 'owner', 'sharing_status', 'sharing_status_display',
            'created_at', 'updated_at'
        ]
        # column_metadata'yı create işleminde ViewSet içinde dolduracağımız için read_only olması daha doğru.
        read_only_fields = ['id', 'column_metadata', 'created_at', 'updated_at']

    def validate_sql_query(self, value):
        """
        SQL Injection'a karşı ilk savunma hattımız. Bu kural değişmedi ve hala kritik.
        """
        query = value.strip().upper()
        if not query.startswith('SELECT'):
            raise serializers.ValidationError("Güvenlik nedeniyle yalnızca 'SELECT' sorgularına izin verilmektedir.")
        
        if ';' in value.strip():
            raise serializers.ValidationError("Güvenlik nedeniyle sorgu içinde çoklu komutlara izin verilmez (;).")

        return value