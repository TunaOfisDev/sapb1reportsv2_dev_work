# backend/productconfig_simulator/admin/simulated_variant_admin.py
from django.contrib import admin
from django.utils.html import format_html
from ..admin.filters import ModelRelatedFilter


class SimulatedVariantAdmin(admin.ModelAdmin):
    """
    Simüle edilmiş varyantları yönetmek için admin arayüzü
    """
    list_display = (
        'id', 'variant_code', 'product_model_display', 'total_price',
        'old_component_codes_display', 'created_at'
    )
    list_filter = (
        'simulation',
        ModelRelatedFilter,
        'is_active',
    )
    search_fields = ('variant_code', 'variant_description', 'product_model__name')
    readonly_fields = (
        'simulation', 'product_model', 'variant_code', 'variant_description',
        'total_price', 'old_component_codes', 'text_answers', 'created_at', 'updated_at',
        'actual_variant_comparison'
    )
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('simulation', 'product_model', 'is_active')
        }),
        ('Varyant Detayları', {
            'fields': ('variant_code', 'variant_description', 'total_price', 'old_component_codes')
        }),
        ('Cevaplar', {
            'fields': ('text_answers',),
            'classes': ('collapse',),
            'description': 'Bu varyant için yanıtlanan sorular ve cevapları.'
        }),
        ('Karşılaştırma', {
            'fields': ('actual_variant_comparison',),
            'description': 'Gerçek varyant ile karşılaştırma.'
        }),
    )

    def product_model_display(self, obj):
        """Ürün modelini göster"""
        if obj.product_model:
            return obj.product_model.name
        return '-'
    product_model_display.short_description = 'Ürün Modeli'

    def old_component_codes_display(self, obj):
        """Eski bileşen kodlarını göster"""
        if obj.old_component_codes:
            if isinstance(obj.old_component_codes, list):
                return ', '.join(obj.old_component_codes[:3]) + (', ...' if len(obj.old_component_codes) > 3 else '')
            return str(obj.old_component_codes)[:50] + ('...' if len(str(obj.old_component_codes)) > 50 else '')
        return '-'
    old_component_codes_display.short_description = 'Eski Bileşen Kodları'

    def actual_variant_comparison(self, obj):
        """Gerçek varyant ile karşılaştırmayı göster"""
        comparison = obj.compare_with_actual()
        
        if not comparison:
            return "Gerçek varyant karşılaştırması mevcut değil veya karşılaştırılamadı."

        html = """
        <style>
            .comparison-table {
                width: 100%;
                border-collapse: collapse;
            }
            .comparison-table th {
                background-color: #f8f9fa;
                font-weight: bold;
                text-align: left;
                padding: 8px;
                border: 1px solid #dee2e6;
            }
            .comparison-table td {
                padding: 8px;
                border: 1px solid #dee2e6;
            }
            .match {
                background-color: #d4edda;
            }
            .mismatch {
                background-color: #f8d7da;
            }
        </style>
        
        <table class="comparison-table">
            <tr>
                <th>Özellik</th>
                <th>Simülasyon</th>
                <th>Gerçek Varyant</th>
                <th>Eşleşme</th>
            </tr>
        """
        
        # Karşılaştırma satırlarını ekle
        for key, values in comparison.items():
            simulated_value = values.get('simulated', '-')
            actual_value = values.get('actual', '-')
            match = values.get('match', False)
            
            row_class = "match" if match else "mismatch"
            match_icon = "✓" if match else "✗"
            
            html += f"""
            <tr class="{row_class}">
                <td>{key}</td>
                <td>{simulated_value}</td>
                <td>{actual_value}</td>
                <td style="text-align: center;">{match_icon}</td>
            </tr>
            """
        
        html += "</table>"
        
        return format_html(html)
    actual_variant_comparison.short_description = 'Gerçek Varyant Karşılaştırması'