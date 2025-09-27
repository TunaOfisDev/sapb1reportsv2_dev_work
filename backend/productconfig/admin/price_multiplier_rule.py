# backend/productconfig/admin/price_multiplier_rule.py
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from ..models import PriceMultiplierRule, Option

class PriceMultiplierRuleResource(resources.ModelResource):
    """
    PriceMultiplierRule için Import/Export kaynağı.
    Excel içe/dışa aktarım desteği sağlar.
    """
    target_options = fields.Field(
        column_name='hedef_secenekler',
        attribute='target_options',
        widget=ManyToManyWidget(Option, field='name', separator='|')
    )

    trigger_options = fields.Field(
        column_name='tetikleyici_secenekler',
        attribute='trigger_options',
        widget=ManyToManyWidget(Option, field='name', separator='|')
    )

    class Meta:
        model = PriceMultiplierRule
        import_id_fields = ('name',)
        export_order = (
            'id', 'name', 'target_options', 'trigger_options', 
            'multiplier_factor', 'logical_operator', 'min_trigger_count',
            'order', 'is_active', 'created_at', 'updated_at'
        )
        skip_unchanged = True
        report_skipped = True
        exclude = ('id',)

@admin.register(PriceMultiplierRule)
class PriceMultiplierRuleAdmin(ImportExportModelAdmin):
    """
    PriceMultiplierRule modeli için admin panel ayarları.
    """
    resource_class = PriceMultiplierRuleResource

    list_display = [
        'id',
        'name', 
        'get_target_options',
        'multiplier_factor', 
        'logical_operator', 
        'min_trigger_count', 
        'get_trigger_options', 
        'is_active', 
        'order'
    ]

    list_filter = [
        'logical_operator',
        'is_active', 
        'multiplier_factor',
        'target_options',
        'trigger_options'
    ]

    search_fields = [
        'name',
        'target_options__name',
        'description'
    ]

    filter_horizontal = [
        'target_options',
        'trigger_options'
    ]

    readonly_fields = [
        'created_at', 
        'updated_at'
    ]

    list_editable = [
        'multiplier_factor',
        'logical_operator',
        'min_trigger_count',
        'order', 
        'is_active'
    ]

    list_per_page = 20

    save_on_top = True
    
    ordering = ['order', 'name']

    def get_target_options(self, obj):
        try:
            return ", ".join([opt.name for opt in obj.target_options.all()[:5]])
        except RecursionError:
            return "Recursive Error Detected"

    def get_trigger_options(self, obj):
        try:
            return ", ".join([opt.name for opt in obj.trigger_options.all()[:5]])
        except RecursionError:
            return "Recursive Error Detected"


    def save_model(self, request, obj, form, change):
        """
        Model kaydedilmeden önce bazı kontroller yapar.
        """
        # Hedef seçeneklerin tetikleyiciler arasında olmaması kontrolü
        for target_option in obj.target_options.all():
            if target_option in obj.trigger_options.all():
                self.message_user(
                    request,
                    _(f"Hedef seçenek '{target_option.name}' tetikleyici seçenekler arasında olamaz!"),
                    level='ERROR'
                )
                return

        # Minimum tetikleyici sayısının geçerli olduğunu kontrol et
        trigger_count = obj.trigger_options.count()
        if trigger_count > 0 and obj.min_trigger_count > trigger_count:
            self.message_user(
                request,
                _("Minimum tetikleyici sayısı, seçili tetikleyici sayısından büyük olamaz!"),
                level='ERROR'
            )
            return

        super().save_model(request, obj, form, change)

    def save_model(self, request, obj, form, change):
        """
        Model kaydedilmeden önce bazı kontroller yapar.
        """
        # İlk olarak nesneyi kaydet
        super().save_model(request, obj, form, change)

        # Kaydedildikten sonra ManyToMany ilişkileri kontrol edin
        trigger_ids = set(obj.trigger_options.values_list('id', flat=True))
        target_ids = set(obj.target_options.values_list('id', flat=True))

        # Hedef seçeneklerin tetikleyiciler arasında olmaması kontrolü
        if trigger_ids.intersection(target_ids):
            self.message_user(
                request,
                _("Hedef seçenekler tetikleyici seçenekler arasında olamaz."),
                level="ERROR"
            )
            return


    def get_form(self, request, obj=None, **kwargs):
        """Form alanlarını düzenler"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['multiplier_factor'].help_text = _(
            "Hedef seçeneklerin fiyatı bu değer ile çarpılacak (0.01-100.00)"
        )
        form.base_fields['logical_operator'].help_text = _(
            "VE: Tüm tetikleyiciler seçili olmalı, VEYA: Herhangi biri seçili olabilir"
        )
        form.base_fields['min_trigger_count'].help_text = _(
            "Kuralın tetiklenmesi için gereken minimum seçenek sayısı"
        )
        return form

    def get_export_filename(self, request, queryset, file_format):
        """Excel export dosya adını özelleştir"""
        date_str = timezone.now().strftime('%Y-%m-%d')
        return f"fiyat-carpan-kurallari-{date_str}.{file_format.get_extension()}"

    def get_export_queryset(self, request):
        """Export edilecek kayıtları filtrele"""
        return self.get_queryset(request).filter(is_active=True)