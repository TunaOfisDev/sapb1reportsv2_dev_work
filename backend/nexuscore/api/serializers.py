# path: backend/nexuscore/api/serializers.py

from rest_framework import serializers

from ..models import (
    DynamicDBConnection, 
    VirtualTable, 
    SharingStatus, 
    ReportTemplate,
    DataApp, 
    AppRelationship,
    # YENİ: Dinamik eşleştirme modelimizi de buraya alıyoruz
    DBTypeMapping 
)
from ..utils.popular_db_list import SUPPORTED_DB_VALUES
from ..services import connection_manager

# --- YENİ: Veri Tipi Eşleştirme için Serializer ---
class DBTypeMappingSerializer(serializers.ModelSerializer):
    """
    DBTypeMapping modeli için serileştirici.
    Yönetici panelinde veri tipi eşleştirmelerini yönetmek için kullanılır.
    """
    class Meta:
        model = DBTypeMapping
        fields = ['id', 'db_type', 'source_type', 'general_category']
        read_only_fields = ['id', 'source_type']


# --- 1. Dinamik Veri Tabanı Bağlantısı için Serializer ---
class DynamicDBConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicDBConnection
        fields = ['id', 'title', 'db_type', 'is_active', 'config_json', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
        extra_kwargs = { 'config_json': {'required': True} }
    
    def validate_db_type(self, value):
        # ... (bu metot aynı kalıyor) ...
        if value not in SUPPORTED_DB_VALUES:
            raise serializers.ValidationError(
                f"Geçersiz veritabanı türü: '{value}'. Desteklenen türlerden biri olmalıdır."
            )
        return value

    # !!! KALICI ÖNLEM BURADA BAŞLIYOR !!!
    def validate_config_json(self, value):
        """
        config_json alanının Django'nun beklediği temel anahtarları içerdiğini doğrular.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Yapılandırma bir JSON nesnesi (sözlük) olmalıdır.")
        
        required_keys = ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST']
        
        missing_keys = [key for key in required_keys if key not in value]
        
        if missing_keys:
            raise serializers.ValidationError(
                f"Yapılandırma JSON içinde şu zorunlu anahtarlar eksik: {', '.join(missing_keys)}"
            )
            
        return value

# --- 2. Sanal Tablo için Serializer ---
# KRİTİK GÜNCELLEME: create metodu burada değiştirildi!
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
        fields = ['id', 'title', 'connection', 'connection_id', 'connection_display', 'sql_query', 'column_metadata', 'owner', 'sharing_status', 'sharing_status_display', 'created_at', 'updated_at']
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
      # Bu kısım tam olarak istediğimiz gibi.
      # "connection" ve "sql_query" bilgilerini alıp...
      user = self.context['request'].user
      connection = validated_data.get('connection')
      sql_query = validated_data.get('sql_query')
      
      # ... az önce yazdığımız zeki "veri dedektifi" fonksiyonunu çağırıyor.
      result = connection_manager.generate_metadata_for_query(connection, sql_query)

      if not result.get('success'):
          raise serializers.ValidationError({
              "sql_query": f"Sorgu çalıştırılamadı: {result.get('error')}"
          })
      
      # Sonucu alıp 'column_metadata' alanına kaydediyor.
      validated_data['column_metadata'] = result.get('metadata')
      validated_data['owner'] = user
      
      return super().create(validated_data)
    

    def update(self, instance, validated_data):
        # 'sql_query' alanı gelen veride var mı diye kontrol et.
        new_sql_query = validated_data.get('sql_query')
        
        # Eğer sorgu değişmişse, meta veriyi yeniden oluştur.
        if new_sql_query and new_sql_query != instance.sql_query:
            connection = instance.connection # Bağlantı değişmez, mevcudu kullan.
            
            # Zeki dedektifimizi tekrar göreve çağırıyoruz!
            result = connection_manager.generate_metadata_for_query(connection, new_sql_query)
            
            if not result.get('success'):
                raise serializers.ValidationError({
                    "sql_query": f"Yeni sorgu çalıştırılamadı: {result.get('error')}"
                })
            
            # Yeni meta veriyi instance üzerine yaz.
            instance.column_metadata = result.get('metadata')

        # Diğer tüm alanları normal şekilde güncelle.
        return super().update(instance, validated_data)


# --- 3. Uygulama İlişkileri için Serializer ---
class AppRelationshipSerializer(serializers.ModelSerializer):
    """
    DataApp içindeki JOIN ilişkilerini yönetir.
    """
    left_table_display = serializers.StringRelatedField(source='left_table', read_only=True)
    right_table_display = serializers.StringRelatedField(source='right_table', read_only=True)
    join_type_display = serializers.CharField(source='get_join_type_display', read_only=True)

    class Meta:
        model = AppRelationship
        fields = ['id', 'app', 'left_table', 'left_table_display', 'left_column', 'right_table', 'right_table_display', 'right_column', 'join_type', 'join_type_display']
        read_only_fields = ['id', 'left_table_display', 'right_table_display', 'join_type_display']

    def validate(self, data):
        app = data.get('app')
        left_table = data.get('left_table')
        right_table = data.get('right_table')

        if left_table.connection != app.connection:
            raise serializers.ValidationError(f"Sol tablo ({left_table.title}), uygulamanın ana bağlantısından ({app.connection.title}) farklı bir kaynağa ait olamaz.")
        if right_table.connection != app.connection:
            raise serializers.ValidationError(f"Sağ tablo ({right_table.title}), uygulamanın ana bağlantısından ({app.connection.title}) farklı bir kaynağa ait olamaz.")
        return data


# --- 4. Playground için İÇ İÇE (NESTED) Sanal Tablo Serializer ---
class VirtualTableNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualTable
        fields = ['id', 'title', 'column_metadata']
        read_only = True


# --- 5. Veri Uygulaması (DataApp) için Serializer ---
class DataAppSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)
    connection_display = serializers.StringRelatedField(source='connection', read_only=True)
    connection_id = serializers.PrimaryKeyRelatedField(
        queryset=DynamicDBConnection.objects.filter(is_active=True),
        source='connection',
        write_only=True,
        label="Veri Kaynağı Bağlantısı"
    )

    virtual_tables = serializers.PrimaryKeyRelatedField(
        queryset=VirtualTable.objects.all(),
        many=True,
        label="İçerilen Sanal Tablolar"
    )
    virtual_tables_display = serializers.StringRelatedField(
        source='virtual_tables',
        many=True,
        read_only=True
    )
    virtual_table_details = VirtualTableNestedSerializer(
        source='virtual_tables',
        many=True, 
        read_only=True
    )
    relationships = AppRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = DataApp
        fields = ['id', 'title', 'description', 'owner', 'connection_id', 'connection_display', 'virtual_tables', 'virtual_tables_display', 'virtual_table_details', 'relationships', 'sharing_status', 'sharing_status_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'relationships', 'created_at', 'updated_at', 'virtual_tables_display', 'virtual_table_details']

    def validate(self, data):
        connection = data.get('connection')
        if not connection and self.instance:
            connection = self.instance.connection

        if 'virtual_tables' in data:
            tables = data.get('virtual_tables')
            for table in tables:
                if table.connection != connection:
                    raise serializers.ValidationError({"virtual_tables": f"Tablo '{table.title}' (ID: {table.id}), bu uygulamanın ana bağlantısı olan '{connection.title}' ile aynı veri kaynağını kullanmıyor."})
        
        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


# --- 6. Rapor Şablonları için Serializer ---
class ReportTemplateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)
    
    source_data_app_display = serializers.StringRelatedField(source='source_data_app', read_only=True)
    source_data_app = serializers.PrimaryKeyRelatedField(read_only=True)
    source_data_app_id = serializers.PrimaryKeyRelatedField(
        queryset=DataApp.objects.all(),
        source='source_data_app',
        write_only=True,
        label="Kaynak Veri Uygulaması ID"
    )

    class Meta:
        model = ReportTemplate
        fields = ['id', 'title', 'description', 'owner', 'source_data_app', 'source_data_app_id', 'source_data_app_display', 'configuration_json', 'sharing_status', 'sharing_status_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']