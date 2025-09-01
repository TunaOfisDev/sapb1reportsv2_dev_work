# path: backend/nexuscore/api/serializers.py

from rest_framework import serializers
# ### YENİ: Yeni modelimizi import ediyoruz ###
from ..models import DynamicDBConnection, VirtualTable, SharingStatus, ReportTemplate
from ..services import connection_manager


# --- 1. Dinamik Veri Tabanı Bağlantısı için Serializer ---

class DynamicDBConnectionSerializer(serializers.ModelSerializer):
    """
    DynamicDBConnection modeli için veri doğrulama ve dönüştürme işlemleri.
    Kayıt sırasında bağlantıyı test ETMEZ. Test, ViewSet'teki özel aksiyon ile yapılır.
    """
    class Meta:
        model = DynamicDBConnection
        fields = [
            'id', 'title', 'db_type', 'is_active', 'config_json',
            'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
        extra_kwargs = {
            'config_json': {'required': True}
        }

# --- 2. Sanal Tablo için Serializer ---

class VirtualTableSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    connection_display = serializers.StringRelatedField(source='connection', read_only=True)
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)
    connection = serializers.PrimaryKeyRelatedField(read_only=True)
    connection_id = serializers.PrimaryKeyRelatedField(
        queryset=DynamicDBConnection.objects.filter(is_active=True), 
        source='connection', 
        write_only=True,
        label="Bağlantı ID"
    )
    
    class Meta:
        model = VirtualTable
        fields = [
            'id', 'title', 'connection', 'connection_id', 'connection_display', 
            'sql_query', 'column_metadata', 'owner', 'sharing_status', 
            'sharing_status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'column_metadata', 'owner', 'created_at', 'updated_at']
        extra_kwargs = { 'sql_query': {'required': True} }

    def validate_sql_query(self, value):
        cleaned_query = value.strip()
        if cleaned_query.endswith(';'):
            cleaned_query = cleaned_query[:-1].strip()
        if ';' in cleaned_query:
            raise serializers.ValidationError("Güvenlik nedeniyle sorgu içinde çoklu komutlara izin verilmez (;).")
        
        first_meaningful_line = ""
        for line in cleaned_query.splitlines():
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith('--'):
                first_meaningful_line = stripped_line
                break
        
        normalized_first_line = first_meaningful_line.upper()
        if not (normalized_first_line.startswith('SELECT') or normalized_first_line.startswith('WITH')):
            raise serializers.ValidationError("Güvenlik nedeniyle sorgular 'SELECT' veya 'WITH' ile başlamalıdır (yorum satırları hariç).")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        connection = validated_data.get('connection')
        sql_query = validated_data.get('sql_query')
        result = connection_manager.generate_metadata_for_query(connection, sql_query)

        if not result.get('success'):
            raise serializers.ValidationError({
                "sql_query": f"Sorgu çalıştırılamadı: {result.get('error')}"
            })
        
        validated_data['column_metadata'] = result.get('metadata')
        validated_data['owner'] = user
        return super().create(validated_data)


# --- 3. Rapor Şablonları için Serializer (YENİ) ---

class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    ReportTemplate modeli için veri doğrulama ve dönüştürme işlemleri.
    """
    owner = serializers.ReadOnlyField(source='owner.email')
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)
    
    # Okuma (GET) için, ID yerine okunabilir isimleri gösterelim
    source_virtual_table_display = serializers.StringRelatedField(
        source='source_virtual_table', 
        read_only=True
    )
    
    # ### YENİ: OKUMA İŞLEMİ İÇİN ID ALANI ###
    # Bu alan, GET isteklerinde kaynak sanal tablonun ID'sini döndürür.
    # "Düzenle" butonunun doğru URL'i oluşturması için bu kritiktir.
    source_virtual_table = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    # Yazma (POST/PUT) için, ID ile ilişki kuralım
    source_virtual_table_id = serializers.PrimaryKeyRelatedField(
        queryset=VirtualTable.objects.all(),
        source='source_virtual_table',
        write_only=True,
        label="Kaynak Sanal Tablo ID"
    )

    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'title', 'description', 'owner',
            'source_virtual_table', # ### YENİ: Okuma alanı `fields` listesine eklendi ###
            'source_virtual_table_id', 
            'source_virtual_table_display',
            'configuration_json',
            'sharing_status', 'sharing_status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']