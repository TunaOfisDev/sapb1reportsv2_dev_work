# path: backend/nexuscore/api/serializers.py

from rest_framework import serializers

# ### GÜNCELLEME: Tüm modellerimizi import ediyoruz ###
from ..models import (
    DynamicDBConnection, 
    VirtualTable, 
    SharingStatus, 
    ReportTemplate,
    DataApp,  # YENİ
    AppRelationship # YENİ
)
from ..services import connection_manager


# --- 1. Dinamik Veri Tabanı Bağlantısı için Serializer ---
# (Bu kod bloğu değişmedi, olduğu gibi kalıyor)
class DynamicDBConnectionSerializer(serializers.ModelSerializer):
    """
    DynamicDBConnection modeli için veri doğrulama ve dönüştürme işlemleri.
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
# (Bu kod bloğu değişmedi, sadece yeni serializer'lar için referans olacak)
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


# --- 3. YENİ: Uygulama İlişkileri için Serializer ---

class AppRelationshipSerializer(serializers.ModelSerializer):
    """
    DataApp içindeki JOIN ilişkilerini yönetir.
    Doğrudan AppRelationshipViewSet üzerinden (veya gelecekte nested olarak) kullanılır.
    """
    # Okuma için String gösterimler
    left_table_display = serializers.StringRelatedField(source='left_table', read_only=True)
    right_table_display = serializers.StringRelatedField(source='right_table', read_only=True)
    join_type_display = serializers.CharField(source='get_join_type_display', read_only=True)

    class Meta:
        model = AppRelationship
        fields = [
            'id', 'app', 
            'left_table', 'left_table_display', 'left_column',
            'right_table', 'right_table_display', 'right_column',
            'join_type', 'join_type_display'
        ]
        read_only_fields = ['id', 'left_table_display', 'right_table_display', 'join_type_display']

    def validate(self, data):
        """
        Mimari bütünlüğünü sağlayan en kritik doğrulama.
        """
        # data['app'] POST anında bir DataApp nesnesi olarak gelir.
        app = data.get('app')
        left_table = data.get('left_table')
        right_table = data.get('right_table')

        # 1. Her iki tablo da DataApp'in ana bağlantısını kullanmalıdır.
        if left_table.connection != app.connection:
            raise serializers.ValidationError(
                f"Sol tablo ({left_table.title}), uygulamanın ana bağlantısından ({app.connection.title}) farklı bir kaynağa ait olamaz."
            )
        if right_table.connection != app.connection:
            raise serializers.ValidationError(
                f"Sağ tablo ({right_table.title}), uygulamanın ana bağlantısından ({app.connection.title}) farklı bir kaynağa ait olamaz."
            )

        # 2. Her iki tablo da DataApp'in 'virtual_tables' M2M listesine eklenmiş olmalıdır.
        # Bu kontrol, veritabanı sorgusu gerektirdiği için dikkatli kullanılmalı,
        # ancak API güvenliği için gereklidir. ViewSet'in queryset'i bunu zorunlu kılabilir.
        # Şimdilik yukarıdaki bağlantı kontrolü yeterlidir.

        return data


# --- 4. YENİ: Veri Uygulaması (DataApp) için Serializer ---

class DataAppSerializer(serializers.ModelSerializer):
    """
    DataApp konteyner modelini yönetir. İlişkisel modelimizin kalbidir.
    """
    owner = serializers.ReadOnlyField(source='owner.email')
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)
    
    # Bağlantı için hem okuma hem yazma alanı (VirtualTable'daki gibi)
    connection_display = serializers.StringRelatedField(source='connection', read_only=True)
    connection_id = serializers.PrimaryKeyRelatedField(
        queryset=DynamicDBConnection.objects.filter(is_active=True),
        source='connection',
        write_only=True,
        label="Veri Kaynağı Bağlantısı"
    )

    # Sanal Tablolar: Yazma için ID listesi, Okuma için String listesi
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

    # İlişkiler: GET isteğinde detayları göstermek için Nested Serializer
    relationships = AppRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = DataApp
        fields = [
            'id', 'title', 'description', 'owner',
            'connection_id', 'connection_display',
            'virtual_tables', 'virtual_tables_display',
            'relationships', # Sadece GET detayda görünür
            'sharing_status', 'sharing_status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'relationships', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Modeldeki notumuzu burada uyguluyoruz: Eklenen tüm VirtualTable'lar
        App'in ana bağlantısıyla eşleşmelidir.
        """
        # Güncelleme (PATCH/PUT) anında, instance zaten bir bağlantıya sahiptir.
        # Oluşturma (POST) anında, bağlantı `data` içinde gelir.
        connection = data.get('connection')
        if not connection and self.instance:
            connection = self.instance.connection

        if 'virtual_tables' in data:
            tables = data.get('virtual_tables')
            for table in tables:
                if table.connection != connection:
                    raise serializers.ValidationError({
                        "virtual_tables": f"Tablo '{table.title}' (ID: {table.id}), bu uygulamanın ana bağlantısı olan '{connection.title}' ile aynı veri kaynağını kullanmıyor."
                    })
        
        return data

    def create(self, validated_data):
        # request.user'ı otomatik olarak owner'a ata
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


# --- 5. GÜNCELLENMİŞ: Rapor Şablonları için Serializer ---

class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    ReportTemplate modeli için veri doğrulama ve dönüştürme.
    ARTIK DataApp modeline bağlanacak şekilde güncellendi.
    """
    owner = serializers.ReadOnlyField(source='owner.email')
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)
    
    # --- DEĞİŞİKLİK: 'virtual_table' alanları 'data_app' olarak güncellendi ---

    # Okuma (GET) için, ID yerine okunabilir isimleri gösterelim
    source_data_app_display = serializers.StringRelatedField(
        source='source_data_app', 
        read_only=True
    )
    
    # GET isteklerinde kaynak app'in ID'sini döndür
    source_data_app = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    # Yazma (POST/PUT) için, ID ile ilişki kuralım
    source_data_app_id = serializers.PrimaryKeyRelatedField(
        # TODO: Queryset'i kullanıcının görebildiği App'ler ile kısıtla
        queryset=DataApp.objects.all(),
        source='source_data_app',
        write_only=True,
        label="Kaynak Veri Uygulaması ID"
    )

    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'title', 'description', 'owner',
            'source_data_app', # Okuma alanı (ID)
            'source_data_app_id', # Yazma alanı
            'source_data_app_display', # Okuma alanı (Display)
            'configuration_json',
            'sharing_status', 'sharing_status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']