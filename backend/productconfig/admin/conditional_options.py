# dosya path yolu: backend/productconfig/admin/conditional_options.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models import ConditionalOption
from .resources import GenericResource

class ConditionalOptionResource(GenericResource):
    class Meta:
        model = ConditionalOption


@admin.register(ConditionalOption)
class ConditionalOptionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    ConditionalOption modeli için admin paneli ayarları.
    """
    resource_class = ConditionalOptionResource
    list_display = [
        'name', 'display_mode', 'logical_operator', 'trigger_option_1', 
        'trigger_option_2', 'target_question', 'get_applicable_options'
    ]
    list_filter = ['display_mode', 'logical_operator', 'target_question']
    search_fields = ['name', 'trigger_option_1__name', 'trigger_option_2__name', 'target_question__name']
    filter_horizontal = ['applicable_options']
    exclude = ['created_at', 'updated_at']
    ordering = ['id']

    def get_applicable_options(self, obj):
        """
        Koşullu seçeneklere bağlı olan uygulanabilir seçeneklerin listesi.
        """
        return ", ".join([option.name for option in obj.applicable_options.all()])
    get_applicable_options.short_description = 'Applicable Options'

    def save_model(self, request, obj, form, change):
        """
        ConditionalOption nesnesini kaydederken özel işleme.
        """
        super().save_model(request, obj, form, change)
