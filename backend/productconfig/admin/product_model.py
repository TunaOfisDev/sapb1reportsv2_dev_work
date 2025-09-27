# dosya path yolu: backend/productconfig/admin/product_model.py
from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from ..models import ProductModel, ProcessStatus
from .resources import GenericResource


class ProductModelResource(GenericResource):
    """
    ProductModel modeli için Import-Export kaynağı.
    """
    class Meta:
        model = ProductModel


class ProcessStatusInline(admin.StackedInline):
    """
    ProductModel için ProcessStatus inline görünümü
    """
    model = ProcessStatus
    readonly_fields = [
        'completion_status', 'relation_status',
        'total_questions', 'total_options',
        'last_check', 'completion_percentage'
    ]
    extra = 0
    max_num = 1
    can_delete = False

    def completion_status(self, obj):
        """İlerleme çubuğunu göster"""
        if obj:
            percentage_str = "{:.1f}".format(obj.completion_percentage)
            return format_html(
                '<div style="width:200px; background-color:#f0f0f0; '
                'height:20px; border-radius:10px; overflow:hidden;">'
                '<div style="width:{}%; background-color:{}; height:20px;">'
                '</div></div> {}%',
                obj.completion_percentage,
                self._get_color_for_percentage(obj.completion_percentage),
                percentage_str
            )
        return "-"
    completion_status.short_description = "Tamamlanma Durumu"

    def relation_status(self, obj):
        """İlişki durumlarını göster"""
        if not obj:
            return "-"

        statuses = [
            ('Marka', obj.has_brand_relations),
            ('Grup', obj.has_group_relations),
            ('Kategori', obj.has_category_relations),
            ('Soru', obj.has_question_relations),
            ('Seçenek', obj.has_option_relations)
        ]

        html_parts = []
        for label, status in statuses:
            color = '#28a745' if status else '#dc3545'
            icon = "✓" if status else "✗"
            html_parts.append(
                format_html(
                    '<span style="color:{}; margin-right:10px;">{}: {}</span>',
                    color, label, icon
                )
            )

        return format_html(''.join(html_parts))
    relation_status.short_description = "İlişki Durumları"

    def _get_color_for_percentage(self, percentage):
        """Yüzdeye göre renk belirle"""
        if percentage < 30:
            return '#dc3545'  # Kırmızı
        elif percentage < 70:
            return '#ffc107'  # Sarı
        return '#28a745'  # Yeşil


@admin.register(ProductModel)
class ProductModelAdmin(ImportExportModelAdmin):
    """
    ProductModel modeli için admin panel ayarları.
    """
    resource_class = ProductModelResource
    list_display = [
        'name', 'category', 'id', 'base_price',
        'is_configurable', 'min_price', 'max_price',
        'get_completion_status'
    ]
    list_filter = ['is_configurable', 'category']
    search_fields = ['name', 'category__name']
    ordering = ['category', 'name']
    exclude = ['created_at', 'updated_at']
    inlines = [ProcessStatusInline]

    def get_completion_status(self, obj):
        """Liste görünümünde ilerleme durumunu göster"""
        try:
            status = obj.process_status
            percentage_str = "{:.1f}".format(status.completion_percentage)
            return format_html(
                '<div style="width:100px; background-color:#f0f0f0; '
                'height:20px; border-radius:10px; overflow:hidden;">'
                '<div style="width:{}%; background-color:{}; height:20px;">'
                '</div></div> {}%',
                status.completion_percentage,
                self._get_color_for_percentage(status.completion_percentage),
                percentage_str
            )
        except ProcessStatus.DoesNotExist:
            return "-"
    get_completion_status.short_description = "Tamamlanma Durumu"

    def _get_color_for_percentage(self, percentage):
        """Yüzdeye göre renk belirle"""
        if percentage < 30:
            return '#dc3545'  # Kırmızı
        elif percentage < 70:
            return '#ffc107'  # Sarı
        return '#28a745'  # Yeşil

    def save_model(self, request, obj, form, change):
        """
        Ürün modeli kayıt işlemleri.
        """
        super().save_model(request, obj, form, change)
        # ProcessStatus'u güncelle/oluştur
        process_status, created = ProcessStatus.objects.get_or_create(
            product_model=obj
        )
        process_status.update_status()
