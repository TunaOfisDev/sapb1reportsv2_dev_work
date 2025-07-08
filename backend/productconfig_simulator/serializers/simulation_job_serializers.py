# backend/productconfig_simulator/serializers/simulation_job_serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model

from productconfig.models import (
    Brand, ProductGroup, Category, ProductModel
)

from ..models.simulation_job import SimulationJob
from ..models.simulated_variant import SimulatedVariant
from ..models.simulation_error import SimulationError

User = get_user_model()


class SimulationJobCreateSerializer(serializers.ModelSerializer):
    """
    Simülasyon işi oluşturmak için kullanılan serializer.
    """
    name = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    
    # İlgili modeller için ID'ler
    brand_id = serializers.IntegerField(required=False, allow_null=True)
    product_group_id = serializers.IntegerField(required=False, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    product_model_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = SimulationJob
        fields = [
            'name', 'description', 'level', 
            'brand_id', 'product_group_id', 'category_id', 'product_model_id',
            'max_variants_per_model', 'include_dependent_rules', 
            'include_conditional_options', 'include_price_multipliers'
        ]
    
    def validate(self, data):
        """
        Simülasyon seviyesine göre gerekli alanların varlığını doğrular.
        """
        level = data.get('level')
        if not level:
            raise serializers.ValidationError("Simülasyon seviyesi (level) gereklidir.")
        
        # Seviyeye göre gerekli alanların kontrolü
        if level == 'brand' and not data.get('brand_id'):
            raise serializers.ValidationError("Marka seviyesinde simülasyon için brand_id gereklidir.")
        
        if level == 'product_group' and not data.get('product_group_id'):
            raise serializers.ValidationError("Ürün grubu seviyesinde simülasyon için product_group_id gereklidir.")
        
        if level == 'category' and not data.get('category_id'):
            raise serializers.ValidationError("Kategori seviyesinde simülasyon için category_id gereklidir.")
        
        if level == 'product_model' and not data.get('product_model_id'):
            raise serializers.ValidationError("Ürün modeli seviyesinde simülasyon için product_model_id gereklidir.")
        
        return data
    
    def create(self, validated_data):
        """
        Simülasyon işi ve ilişkili objeler oluşturur.
        """
        # İlgili model nesnelerini getir
        brand_id = validated_data.pop('brand_id', None)
        product_group_id = validated_data.pop('product_group_id', None)
        category_id = validated_data.pop('category_id', None)
        product_model_id = validated_data.pop('product_model_id', None)
        
        # Simülasyon adı otomatik oluşturma
        if not validated_data.get('name'):
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
            level_display = dict(SimulationJob.SimulationLevel.choices).get(validated_data.get('level'), 'Simülasyon')
            validated_data['name'] = f"{level_display} - {timestamp}"
        
        # Simülasyon işini oluştur
        simulation = SimulationJob(**validated_data)
        
        # İlişkili modelleri ayarla
        if brand_id:
            try:
                simulation.brand = Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                raise serializers.ValidationError(f"Brand ID {brand_id} bulunamadı.")
        
        if product_group_id:
            try:
                simulation.product_group = ProductGroup.objects.get(id=product_group_id)
            except ProductGroup.DoesNotExist:
                raise serializers.ValidationError(f"ProductGroup ID {product_group_id} bulunamadı.")
        
        if category_id:
            try:
                simulation.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Category ID {category_id} bulunamadı.")
        
        if product_model_id:
            try:
                simulation.product_model = ProductModel.objects.get(id=product_model_id)
            except ProductModel.DoesNotExist:
                raise serializers.ValidationError(f"ProductModel ID {product_model_id} bulunamadı.")
        
        # Mevcut kullanıcıyı ayarla
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            simulation.created_by = request.user
        
        simulation.save()
        return simulation


class SimulationJobDetailSerializer(serializers.ModelSerializer):
    """
    Simülasyon işinin detaylı bilgilerini sağlayan serializer.
    """
    brand = serializers.StringRelatedField()
    product_group = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    product_model = serializers.StringRelatedField()
    created_by = serializers.StringRelatedField()
    
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    variant_count = serializers.SerializerMethodField()
    error_count = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulationJob
        fields = [
            'id', 'name', 'description', 'level', 'level_display', 
            'status', 'status_display', 'brand', 'product_group', 
            'category', 'product_model', 'max_variants_per_model',
            'include_dependent_rules', 'include_conditional_options', 
            'include_price_multipliers', 'start_time', 'end_time',
            'total_models', 'processed_models', 'total_variants', 
            'total_errors', 'celery_task_id', 'result_summary',
            'variant_count', 'error_count', 'duration', 'progress_percentage',
            'created_by', 'created_at', 'updated_at', 'is_active'
        ]
    
    def get_variant_count(self, obj):
        """Simülasyona ait varyant sayısını döndürür."""
        return SimulatedVariant.objects.filter(simulation=obj).count()
    
    def get_error_count(self, obj):
        """Simülasyona ait hata sayısını döndürür."""
        return SimulationError.objects.filter(simulation=obj).count()
    
    def get_duration(self, obj):
        """Simülasyonun süresini döndürür."""
        if not obj.start_time:
            return None
        
        end = obj.end_time or timezone.now()
        duration_seconds = (end - obj.start_time).total_seconds()
        
        # Süreyi saat:dakika:saniye formatına dönüştür
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'seconds': duration_seconds,
            'formatted': f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        }
    
    def get_progress_percentage(self, obj):
        """Simülasyonun ilerleme yüzdesini döndürür."""
        if obj.status == SimulationJob.SimulationStatus.COMPLETED:
            return 100
        elif obj.status == SimulationJob.SimulationStatus.FAILED:
            # İşlenen model sayısı üzerinden yaklaşık yüzde
            if obj.total_models > 0:
                return int((obj.processed_models / obj.total_models) * 100)
            return 0
        elif obj.status == SimulationJob.SimulationStatus.RUNNING:
            if obj.total_models > 0:
                return int((obj.processed_models / obj.total_models) * 100)
            return 0
        else:
            return 0


class SimulationJobListSerializer(serializers.ModelSerializer):
    """
    Simülasyon işlerinin listelemesi için kullanılan basitleştirilmiş serializer.
    """
    brand = serializers.StringRelatedField()
    product_group = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    product_model = serializers.StringRelatedField()
    
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    duration = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulationJob
        fields = [
            'id', 'name', 'level', 'level_display', 'status', 'status_display', 
            'brand', 'product_group', 'category', 'product_model',
            'total_models', 'processed_models', 'total_variants', 'total_errors',
            'start_time', 'end_time', 'duration', 'progress_percentage',
            'created_at', 'is_active'
        ]
    
    def get_duration(self, obj):
        """Simülasyonun süresini döndürür."""
        if not obj.start_time:
            return None
        
        end = obj.end_time or timezone.now()
        duration_seconds = (end - obj.start_time).total_seconds()
        
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}s {int(minutes)}dk"
        else:
            return f"{int(minutes)}dk {int(seconds)}sn"
    
    def get_progress_percentage(self, obj):
        """Simülasyonun ilerleme yüzdesini döndürür."""
        if obj.status == SimulationJob.SimulationStatus.COMPLETED:
            return 100
        elif obj.status == SimulationJob.SimulationStatus.FAILED:
            # İşlenen model sayısı üzerinden yaklaşık yüzde
            if obj.total_models > 0:
                return int((obj.processed_models / obj.total_models) * 100)
            return 0
        elif obj.status == SimulationJob.SimulationStatus.RUNNING:
            if obj.total_models > 0:
                return int((obj.processed_models / obj.total_models) * 100)
            return 0
        else:
            return 0


class SimulationStatusSerializer(serializers.ModelSerializer):
    """
    Simülasyon durumunu kontrol etmek için basit serializer.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulationJob
        fields = [
            'id', 'status', 'status_display', 'total_models', 'processed_models', 
            'total_variants', 'total_errors', 'start_time', 'end_time', 'progress_percentage'
        ]
    
    def get_progress_percentage(self, obj):
        """Simülasyonun ilerleme yüzdesini döndürür."""
        if obj.status == SimulationJob.SimulationStatus.COMPLETED:
            return 100
        elif obj.status == SimulationJob.SimulationStatus.FAILED:
            # İşlenen model sayısı üzerinden yaklaşık yüzde
            if obj.total_models > 0:
                return int((obj.processed_models / obj.total_models) * 100)
            return 0
        elif obj.status == SimulationJob.SimulationStatus.RUNNING:
            if obj.total_models > 0:
                return int((obj.processed_models / obj.total_models) * 100)
            return 0
        else:
            return 0