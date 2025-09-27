# backend/productconfig/admin/process_status.py
from django.contrib import admin
from django.utils.html import format_html
from django.core.management import call_command
from django.contrib import messages
from import_export import resources, formats
from import_export.admin import ExportMixin
from import_export import fields
from ..models import ProcessStatus
import threading

# Export için Resource sınıfı
class ProcessStatusResource(resources.ModelResource):
    """ProcessStatus modeli için export kaynağı"""
    
    # Temel alanları tanımla
    product_model = fields.Field(
        column_name='Ürün Modeli',
        attribute='product_model',
        widget=resources.widgets.CharWidget()
    )
    
    brand = fields.Field(
        column_name='Marka',
        attribute='product_model__category__brand',
        widget=resources.widgets.CharWidget()
    )
    
    product_group = fields.Field(
        column_name='Ürün Grubu',
        attribute='product_model__category__product_group',
        widget=resources.widgets.CharWidget()
    )
    
    category = fields.Field(
        column_name='Kategori',
        attribute='product_model__category',
        widget=resources.widgets.CharWidget()
    )

    total_questions = fields.Field(
        column_name='Toplam Soru',
        attribute='total_questions'
    )

    total_options = fields.Field(
        column_name='Toplam Seçenek',
        attribute='total_options'
    )

    total_dimension_options = fields.Field(
        column_name='Toplam Ölçü Seçenek',
        attribute='total_dimension_options'
    )

    completion_percentage = fields.Field(
        column_name='Tamamlanma Yüzdesi',
        attribute='completion_percentage'
    )

    last_check = fields.Field(
        column_name='Son Kontrol',
        attribute='last_check'
    )

    class Meta:
        model = ProcessStatus
        fields = (
            'product_model',
            'brand',
            'product_group', 
            'category',
            'total_questions',
            'total_options',
            'total_dimension_options',
            'completion_percentage',
            'last_check'
        )
        export_order = fields

    def dehydrate_product_model(self, obj):
        return obj.product_model.name if obj.product_model else ''

    def dehydrate_brand(self, obj):
        if obj.product_model and obj.product_model.category:
            return obj.product_model.category.brand.name
        return ''

    def dehydrate_product_group(self, obj):
        if obj.product_model and obj.product_model.category:
            return obj.product_model.category.product_group.name
        return ''

    def dehydrate_category(self, obj):
        if obj.product_model and obj.product_model.category:
            return obj.product_model.category.name
        return ''
    
    def dehydrate_completion_percentage(self, obj):
        return f"% {obj.completion_percentage:.1f}"

@admin.register(ProcessStatus)
class ProcessStatusAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ProcessStatusResource
    
    def get_export_formats(self):
        """Dışa aktarma formatlarını belirle"""
        formats_list = [
            formats.base_formats.XLSX,
        ]
        return formats_list

    
   
    list_display = [
        'get_product_model_name',
        'get_brand',          
        'get_product_group',  
        'get_category',       
        'completion_status',
        'relation_status',
        'total_questions',
        'total_options',
        'total_dimension_options',
        'last_check'
    ]
    
    readonly_fields = [
        'completion_percentage',
        'total_questions',
        'total_options',
        'last_check'
    ]
    
    search_fields = [
        'product_model__name',
        'product_model__category__brand__name',
        'product_model__category__product_group__name',
        'product_model__category__name'
    ]
    
    list_filter = [
        'has_brand_relations',
        'has_group_relations',
        'has_category_relations',
        'has_question_relations',
        'has_option_relations',
        ('product_model__category__brand', admin.RelatedOnlyFieldListFilter),
        ('product_model__category__product_group', admin.RelatedOnlyFieldListFilter),
        ('product_model__category', admin.RelatedOnlyFieldListFilter)
    ]

    actions = ['update_all_statuses']

    # Export formatlarını belirle
    formats = ['xlsx']

    def get_product_model_name(self, obj):
        """Sadece ürün modelinin adını gösterir"""
        return obj.product_model.name if obj.product_model else '-'
    get_product_model_name.short_description = 'Ürün Modeli'
    
    def get_brand(self, obj):
        """Ürün modelinin markasını gösterir"""
        if obj.product_model and obj.product_model.category:
            return obj.product_model.category.brand.name
        return '-'
    get_brand.short_description = 'Marka'
    
    def get_product_group(self, obj):
        """Ürün modelinin grubunu gösterir"""
        if obj.product_model and obj.product_model.category:
            return obj.product_model.category.product_group.name
        return '-'
    get_product_group.short_description = 'Ürün Grubu'
    
    def get_category(self, obj):
        """Ürün modelinin kategorisini gösterir"""
        if obj.product_model and obj.product_model.category:
            return obj.product_model.category.name
        return '-'
    get_category.short_description = 'Kategori'

    def update_all_statuses(self, request, queryset):
        """Tüm durumları güncelle"""
        try:
            def run_commands():
                # İlk komutu çalıştır
                call_command('update_all_process_status')
                # İkinci komutu çalıştır
                call_command('sync_process_status', force=True)
                # Kullanıcıya bilgi mesajı göster
                self.message_user(
                    request, 
                    'Tüm durumlar başarıyla güncellendi!',
                    messages.SUCCESS
                )

            # Komutları arka planda çalıştır
            thread = threading.Thread(target=run_commands)
            thread.start()

            # Kullanıcıya işlemin başladığını bildir
            self.message_user(
                request,
                'Güncelleme işlemi başlatıldı. Bu işlem biraz zaman alabilir...',
                messages.INFO
            )

        except Exception as e:
            self.message_user(
                request,
                f'Hata oluştu: {str(e)}',
                messages.ERROR
            )

    update_all_statuses.short_description = "✨ Tüm Durumları Güncelle"

    def completion_status(self, obj):
        """Tamamlanma durumunu görsel olarak gösterir"""
        percentage_str = "{:.1f}".format(obj.completion_percentage)
        return format_html(
            '<div style="width:100px; background-color:#f0f0f0; height:20px; '
            'border-radius:10px; overflow:hidden;">'
            '<div style="width:{}%; background-color:{}; height:20px;"></div>'
            '</div> {}%',
            obj.completion_percentage,
            self._get_color_for_percentage(obj.completion_percentage),
            percentage_str
        )
    completion_status.short_description = "Tamamlanma Durumu"

    def relation_status(self, obj):
        """İlişki durumlarını ikonlarla gösterir"""
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
        """Yüzdeye göre renk döndürür"""
        if percentage < 30:
            return '#dc3545'  # Kırmızı
        elif percentage < 70:
            return '#ffc107'  # Sarı
        else:
            return '#28a745'  # Yeşil

    def save_model(self, request, obj, form, change):
        """Kaydetmeden önce durumu güncelle"""
        obj.update_status()