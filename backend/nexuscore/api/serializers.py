# path: backend/nexuscore/api/serializers.py

from rest_framework import serializers
from ..models import DynamicDBConnection, VirtualTable, SharingStatus
from ..services import connection_manager


class DynamicDBConnectionSerializer(serializers.ModelSerializer):
    """
    DynamicDBConnection modeli için veri doğrulama ve dönüştürme işlemleri.
    YENİ İŞ AKIŞI: Bu serializer artık kaydetme sırasında bağlantıyı test ETMEZ.
    Test işlemi, ViewSet'teki 'test_connection' aksiyonu ile kullanıcı tarafından manuel olarak yapılır.
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

    # `create` metodunu override etmiyoruz. ModelSerializer'ın standart davranışı
    # (veriyi al ve kaydet) bizim için mükemmel. Önleyici test yok.

# --- Sanal Tablo için Serializer ---
# (VirtualTableSerializer'da bir değişiklik yapmaya gerek yok, olduğu gibi kalabilir)
class VirtualTableSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    connection_display = serializers.StringRelatedField(source='connection', read_only=True)
    sharing_status_display = serializers.CharField(source='get_sharing_status_display', read_only=True)

    # ### YENİ: OKUMA İŞLEMİ İÇİN ALAN ###
    # Bu alan, GET isteklerinde connection'ın ID'sini döndürür.
    connection = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # ### MEVCUT: YAZMA İŞLEMİ İÇİN ALAN ###
    # Bu alan, POST/PATCH isteklerinde connection ID'sini almak için kullanılır.
    connection_id = serializers.PrimaryKeyRelatedField(
        queryset=DynamicDBConnection.objects.filter(is_active=True), 
        source='connection', 
        write_only=True,
        label="Bağlantı ID"
    )
    
    class Meta:
        model = VirtualTable
        fields = [
            'id', 'title', 
            'connection',  # ### YENİ: Okuma alanı `fields` listesine eklendi ###
            'connection_id', 'connection_display', 'sql_query', 
            'column_metadata', 'owner', 'sharing_status', 'sharing_status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'column_metadata', 'owner', 'created_at', 'updated_at']
        extra_kwargs = { 'sql_query': {'required': True} }

    def validate_sql_query(self, value):
        """
        SQL Injection'a karşı temel güvenlik doğrulamaları.
        Artık sorgunun başındaki yorum satırlarını ve boşlukları görmezden gelir.
        """
        cleaned_query = value.strip()
        
        # Sonundaki noktalı virgülü geçici olarak kaldıralım
        if cleaned_query.endswith(';'):
            cleaned_query = cleaned_query[:-1].strip()

        # İçinde hala noktalı virgül var mı diye bakalım (çoklu komut engeli)
        if ';' in cleaned_query:
            raise serializers.ValidationError("Güvenlik nedeniyle sorgu içinde çoklu komutlara izin verilmez (;).")

        # Yorumları ve boş satırları atlayarak ilk anlamlı satırı bulalım
        first_meaningful_line = ""
        for line in cleaned_query.splitlines():
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith('--'):
                first_meaningful_line = stripped_line
                break
        
        # İlk anlamlı satırın SELECT veya WITH ile başlayıp başlamadığını kontrol edelim
        normalized_first_line = first_meaningful_line.upper()
        if not (normalized_first_line.startswith('SELECT') or normalized_first_line.startswith('WITH')):
            raise serializers.ValidationError(
                "Güvenlik nedeniyle sorgular 'SELECT' veya 'WITH' ile başlamalıdır (yorum satırları hariç)."
            )
        
        return value # Orijinal, yorumlu halini kaydedelim.

    # ### NİHAİ DÜZELTME: Tüm `create` mantığı artık burada ###
    def create(self, validated_data):
        # `owner` bilgisi, `save()` metodundan (ViewSet'ten) buraya gelir.
        user = self.context['request'].user
        
        connection = validated_data.get('connection')
        sql_query = validated_data.get('sql_query')

        # Servis katmanını çağırarak sorgudan meta veriyi (kolon isimleri) al.
        result = connection_manager.generate_metadata_for_query(connection, sql_query)

        if not result.get('success'):
            # Eğer sorgu hatalıysa, validation error fırlat.
            raise serializers.ValidationError({
                "sql_query": f"Sorgu çalıştırılamadı: {result.get('error')}"
            })
        
        # Meta veriyi ve sahibi `validated_data`'ya ekle.
        validated_data['column_metadata'] = result.get('metadata')
        validated_data['owner'] = user
        
        # Üst sınıfın `create` metodunu çağırarak nesneyi oluştur.
        return super().create(validated_data)