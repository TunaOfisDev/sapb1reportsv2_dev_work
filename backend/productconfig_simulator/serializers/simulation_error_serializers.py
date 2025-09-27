#  backend/productconfig_simulator/serializers/simulation_error_serializers.py
from rest_framework import serializers
from django.utils import timezone

from productconfig.models import (
    ProductModel, Question, Option
)

from ..models.simulation_error import SimulationError
from ..utils.error_helpers import SimulationErrorHelper


class SimulationErrorSerializer(serializers.ModelSerializer):
    """
    Simülasyon hataları için temel serializer.
    """
    error_type_display = serializers.CharField(source='get_error_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    product_model_name = serializers.SerializerMethodField()
    question_name = serializers.SerializerMethodField()
    option_name = serializers.SerializerMethodField()
    
    fix_suggestions = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulationError
        fields = [
            'id', 'simulation', 'error_type', 'error_type_display',
            'severity', 'severity_display', 'message', 'details',
            'product_model', 'product_model_name', 'question', 'question_name',
            'option', 'option_name', 'resolution_status', 'fix_suggestions',
            'created_at'
        ]
    
    def get_product_model_name(self, obj):
        """Ürün modeli adını döndürür."""
        return obj.product_model.name if obj.product_model else None
    
    def get_question_name(self, obj):
        """Soru adını döndürür."""
        return obj.question.name if obj.question else None
    
    def get_option_name(self, obj):
        """Seçenek adını döndürür."""
        return obj.option.name if obj.option else None
    
    def get_fix_suggestions(self, obj):
        """Hata için çözüm önerileri döndürür."""
        helper = SimulationErrorHelper()
        return helper.generate_error_fix_suggestions(obj)


class SimulationErrorDetailSerializer(serializers.ModelSerializer):
    """
    Simülasyon hatalarının detaylı görüntülenmesi için serializer.
    """
    error_type_display = serializers.CharField(source='get_error_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    product_model_data = serializers.SerializerMethodField()
    question_data = serializers.SerializerMethodField()
    option_data = serializers.SerializerMethodField()
    
    fix_suggestions = serializers.SerializerMethodField()
    resolution_data = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulationError
        fields = [
            'id', 'simulation', 'error_type', 'error_type_display',
            'severity', 'severity_display', 'message', 'details',
            'product_model', 'product_model_data', 'question', 'question_data',
            'option', 'option_data', 'resolution_status', 'fix_suggestions',
            'resolution_data', 'created_at', 'updated_at'
        ]
    
    def get_product_model_data(self, obj):
        """Ürün modeli verilerini döndürür."""
        if not obj.product_model:
            return None
        
        return {
            'id': obj.product_model.id,
            'name': obj.product_model.name,
            'category': obj.product_model.category.name if obj.product_model.category else None,
            'base_price': str(obj.product_model.base_price) if obj.product_model.base_price else '0',
        }
    
    def get_question_data(self, obj):
        """Soru verilerini döndürür."""
        if not obj.question:
            return None
        
        return {
            'id': obj.question.id,
            'name': obj.question.name,
            'question_type': obj.question.question_type,
            'category_type': obj.question.category_type,
            'is_required': obj.question.is_required
        }
    
    def get_option_data(self, obj):
        """Seçenek verilerini döndürür."""
        if not obj.option:
            return None
        
        return {
            'id': obj.option.id,
            'name': obj.option.name,
            'option_type': obj.option.option_type,
            'price_modifier': str(obj.option.price_modifier) if obj.option.price_modifier else '0'
        }
    
    def get_fix_suggestions(self, obj):
        """Hata için çözüm önerileri döndürür."""
        helper = SimulationErrorHelper()
        return helper.generate_error_fix_suggestions(obj)
    
    def get_resolution_data(self, obj):
        """Çözüm verilerini döndürür."""
        if not obj.resolution_status:
            return None
        
        return {
            'resolved_by': obj.resolved_by.username if obj.resolved_by else None,
            'resolved_at': obj.resolved_at.isoformat() if obj.resolved_at else None,
            'resolution_notes': obj.resolution_notes
        }


class SimulationErrorListSerializer(serializers.ModelSerializer):
    """
    Simülasyon hatalarının listelenmesi için basitleştirilmiş serializer.
    """
    error_type_display = serializers.CharField(source='get_error_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    related_info = serializers.SerializerMethodField()
    
    class Meta:
        model = SimulationError
        fields = [
            'id', 'simulation', 'error_type', 'error_type_display',
            'severity', 'severity_display', 'message', 'related_info',
            'resolution_status', 'created_at'
        ]
    
    def get_related_info(self, obj):
        """İlgili nesnelerin bilgilerini döndürür."""
        related_info = {}
        
        if obj.product_model:
            related_info['product_model'] = {
                'id': obj.product_model.id,
                'name': obj.product_model.name
            }
        
        if obj.question:
            related_info['question'] = {
                'id': obj.question.id,
                'name': obj.question.name
            }
        
        if obj.option:
            related_info['option'] = {
                'id': obj.option.id,
                'name': obj.option.name
            }
        
        return related_info


class SimulationErrorResolveSerializer(serializers.ModelSerializer):
    """
    Simülasyon hatalarının çözüldü olarak işaretlenmesi için serializer.
    """
    resolution_notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = SimulationError
        fields = ['resolution_notes']
    
    def update(self, instance, validated_data):
        """
        Hatayı çözüldü olarak işaretler.
        """
        instance.resolution_status = True
        instance.resolved_at = timezone.now()
        
        # Çözüm notlarını kaydet (varsa)
        if 'resolution_notes' in validated_data:
            instance.resolution_notes = validated_data['resolution_notes']
        
        # Çözen kullanıcıyı kaydet (varsa)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            instance.resolved_by = request.user
        
        instance.save()
        return instance


class SimulationErrorBulkResolveSerializer(serializers.Serializer):
    """
    Birden çok simülasyon hatasını toplu olarak çözüldü işaretlemek için serializer.
    """
    error_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    resolution_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_error_ids(self, value):
        """
        Belirtilen hata ID'lerinin geçerli olduğunu doğrular.
        """
        errors = SimulationError.objects.filter(id__in=value, resolution_status=False)
        if errors.count() != len(value):
            missing_ids = set(value) - set(errors.values_list('id', flat=True))
            raise serializers.ValidationError(
                f"Şu ID'lere sahip hatalar bulunamadı veya zaten çözülmüş: {missing_ids}"
            )
        return value
    
    def save(self):
        """
        Belirtilen hataları çözüldü olarak işaretler.
        """
        error_ids = self.validated_data['error_ids']
        resolution_notes = self.validated_data.get('resolution_notes', '')
        
        # Çözen kullanıcıyı al
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        # Toplu güncelleme
        errors = SimulationError.objects.filter(id__in=error_ids, resolution_status=False)
        
        for error in errors:
            error.resolution_status = True
            error.resolved_at = timezone.now()
            error.resolution_notes = resolution_notes
            if user:
                error.resolved_by = user
            error.save()
        
        return {
            'resolved_count': errors.count(),
            'error_ids': error_ids
        }