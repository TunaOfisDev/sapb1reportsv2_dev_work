# dosya path yolu: backend/productconfig/admin/question.py
from django.contrib import admin
from import_export.admin import ImportExportMixin  # Import ve Export için doğru mixin
from ..models import Question
from .resources import GenericResource


class QuestionResource(GenericResource):
    """
    Question modeli için Import-Export kaynağı.
    """
    class Meta:
        model = Question


@admin.register(Question)
class QuestionAdmin(ImportExportMixin, admin.ModelAdmin):  # ExportMixin yerine ImportExportMixin kullanılıyor
    """
    Question modeli için admin paneli ayarları.
    """
    resource_class = QuestionResource
    list_display = [
        'name', 'id', 'question_type', 'category_type', 
        'order', 'variant_order', 'is_required', 'is_active'
    ]
    list_editable = ['order', 'variant_order']
    list_filter = ['question_type', 'category_type', 'is_active', 'applicable_groups']  # applicable_groups filtresi eklendi
    search_fields = ['name']
    ordering = ['order', 'variant_order']
    filter_horizontal = ['applicable_brands', 'applicable_categories', 'applicable_product_models', 'applicable_groups']  # applicable_groups eklendi
    exclude = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """
        Question modeli kayıt işlemleri.
        """
        super().save_model(request, obj, form, change)

