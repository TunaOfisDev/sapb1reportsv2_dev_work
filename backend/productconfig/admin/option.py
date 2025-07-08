# backend/productconfig/admin/option.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models import Option
from .resources import GenericResource
from import_export.fields import Field
from django.db.models import Count

class OptionResource(GenericResource):
    """Option modeli için Import-Export kaynağı."""
    # Mevcut alanlar
    applicable_brands_names = Field(attribute='applicable_brands', column_name='Applicable Brands (Names)')
    applicable_groups_names = Field(attribute='applicable_groups', column_name='Applicable Groups (Names)')
    applicable_categories_names = Field(attribute='applicable_categories', column_name='Applicable Categories (Names)')
    applicable_product_models_names = Field(attribute='applicable_product_models', column_name='Applicable Product Models (Names)')

    # Tetikleyici seçenekler için yeni alanlar
    melamine_triggers_names = Field(attribute='melamine_triggers', column_name='Melamine Triggers')
    laminate_triggers_names = Field(attribute='laminate_triggers', column_name='Laminate Triggers')
    veneer_triggers_names = Field(attribute='veneer_triggers', column_name='Veneer Triggers')
    lacquer_triggers_names = Field(attribute='lacquer_triggers', column_name='Lacquer Triggers')

    # Soru İlişki Sayısı alanı
    question_relation_count = Field(
        column_name='Soru İlişki Sayısı',
        attribute='question_relation_count'
    )

    class Meta:
        model = Option
        fields = (
            'id',
            'is_active',
            'name',
            'option_type',
            'price_modifier',
            'normal_price',
            'price_melamine',
            'price_laminate',
            'price_veneer',
            'price_lacquer',
            'color_status',
            'variant_code_part',
            'variant_description_part',
            'image',
            'is_popular',
            'melamine_triggers',
            'laminate_triggers',
            'veneer_triggers',
            'lacquer_triggers',
            'applicable_brands',
            'applicable_groups',
            'applicable_categories',
            'applicable_product_models',
            'applicable_brands_names',
            'applicable_groups_names',
            'applicable_categories_names',
            'applicable_product_models_names',
            'melamine_triggers_names',
            'laminate_triggers_names',
            'veneer_triggers_names',
            'lacquer_triggers_names',
            'question_relation_count'
        )
        export_order = fields

    def get_export_headers(self, *args, **kwargs):
        headers = super().get_export_headers(*args, **kwargs)
        return headers

    # Question relation count için özel dehydrate metodu
    def dehydrate_question_relation_count(self, obj):
        return obj.question_option_relations.count()

    # Mevcut metodlar
    def dehydrate_applicable_brands_names(self, option):
        return ", ".join([brand.name for brand in option.applicable_brands.all()])

    def dehydrate_applicable_groups_names(self, option):
        return ", ".join([group.name for group in option.applicable_groups.all()])

    def dehydrate_applicable_categories_names(self, option):
        return ", ".join([category.name for category in option.applicable_categories.all()])

    def dehydrate_applicable_product_models_names(self, option):
        return ", ".join([model.name for model in option.applicable_product_models.all()])

    # Tetikleyiciler için metodlar
    def dehydrate_melamine_triggers_names(self, option):
        return ", ".join([opt.name for opt in option.melamine_triggers.all()])

    def dehydrate_laminate_triggers_names(self, option):
        return ", ".join([opt.name for opt in option.laminate_triggers.all()])

    def dehydrate_veneer_triggers_names(self, option):
        return ", ".join([opt.name for opt in option.veneer_triggers.all()])

    def dehydrate_lacquer_triggers_names(self, option):
        return ", ".join([opt.name for opt in option.lacquer_triggers.all()])

class QuestionCountFilter(admin.SimpleListFilter):
    title = 'Soru İlişki Sayısı'
    parameter_name = 'question_count'

    def lookups(self, request, model_admin):
        return (
            ('0', '0 Soru'),
            ('1', '1 Soru'),
            ('2', '2 Soru'),
            ('3', '3 Soru'),
            ('4', '4 Soru'),
            ('5+', '5+ Soru'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(q_count=Count('question_option_relations'))
        
        if self.value() == '0':
            return queryset.filter(q_count=0)
        elif self.value() == '1':
            return queryset.filter(q_count=1)
        elif self.value() == '2':
            return queryset.filter(q_count=2)
        elif self.value() == '3':
            return queryset.filter(q_count=3)
        elif self.value() == '4':
            return queryset.filter(q_count=4)
        elif self.value() == '5+':
            return queryset.filter(q_count__gte=5)
        return queryset

@admin.register(Option)
class OptionAdmin(ImportExportModelAdmin):
    resource_class = OptionResource

    actions = ['calculate_question_relations']
    
    @admin.action(description='Seçili seçenekler için soru ilişki sayısını hesapla')
    def calculate_question_relations(self, request, queryset):
        updated = 0
        for option in queryset:
            relation_count = option.question_option_relations.count()
            # İsterseniz burada bir field'a kaydedebilirsiniz
            # option.question_relation_count = relation_count
            # option.save()
            updated += 1
            
        self.message_user(
            request,
            f'{updated} seçenek için soru ilişki sayısı hesaplandı.',
            level='SUCCESS'
        )

    # Liste görünümü alanları
    list_display = [
        'name', 'id', 'option_type',
        'normal_price',
        'price_melamine', 'price_laminate', 'price_veneer', 'price_lacquer',
        'variant_code_part', 'variant_description_part', 'color_status',
        'is_active', 'get_related_brands', 'get_related_groups',
        'get_related_categories', 'get_related_product_models',
        'get_melamine_triggers', 'get_laminate_triggers',
        'get_veneer_triggers', 'get_lacquer_triggers',
        'get_question_count',  # Soru ilişki sayısı
        'created_at', 'updated_at'
    ]

    # Filtreler - QuestionCountFilter eklendi
    list_filter = [
        'option_type', 'is_active', 'color_status',
        'applicable_brands', 'applicable_groups',
        'applicable_categories', 'applicable_product_models',
        QuestionCountFilter
    ]
 

    # Arama alanları
    search_fields = ['name', 'variant_code_part', 'variant_description_part']

    # Sıralama
    ordering = ['id']

    # Çoklu seçim alanları
    filter_horizontal = [
        'applicable_brands', 'applicable_groups',
        'applicable_categories', 'applicable_product_models',
        'melamine_triggers', 'laminate_triggers',
        'veneer_triggers', 'lacquer_triggers'
    ]

    # Form görünümünden çıkarılacak alanlar
    exclude = ['created_at', 'updated_at', 'price_modifier']

    def save_model(self, request, obj, form, change):
        """
        Option kaydedilirken ManyToMany ilişkilerinin doğru şekilde işlenmesini sağlar.
        """
        # İlk olarak temel objeyi kaydet
        if not obj.pk:  # Yeni kayıt kontrolü
            super().save_model(request, obj, form, change)

        # ManyToMany alanları kaydet
        if form.cleaned_data.get('melamine_triggers'):
            obj.melamine_triggers.set(form.cleaned_data['melamine_triggers'])
        if form.cleaned_data.get('laminate_triggers'):
            obj.laminate_triggers.set(form.cleaned_data['laminate_triggers'])
        if form.cleaned_data.get('veneer_triggers'):
            obj.veneer_triggers.set(form.cleaned_data['veneer_triggers'])
        if form.cleaned_data.get('lacquer_triggers'):
            obj.lacquer_triggers.set(form.cleaned_data['lacquer_triggers'])

        # Diğer ManyToMany alanlarını da işleyin
        if form.cleaned_data.get('applicable_brands'):
            obj.applicable_brands.set(form.cleaned_data['applicable_brands'])
        if form.cleaned_data.get('applicable_groups'):
            obj.applicable_groups.set(form.cleaned_data['applicable_groups'])
        if form.cleaned_data.get('applicable_categories'):
            obj.applicable_categories.set(form.cleaned_data['applicable_categories'])
        if form.cleaned_data.get('applicable_product_models'):
            obj.applicable_product_models.set(form.cleaned_data['applicable_product_models'])

        super().save_model(request, obj, form, change)

    # Yeni metod: Soru ilişki sayısını gösterir
    def get_question_count(self, obj):
        """Seçenek ile ilişkili soru sayısını döndürür."""
        return obj.question_option_relations.count()
    get_question_count.short_description = 'Soru İlişki Sayısı'

    # Mevcut get_related metodları
    def get_related_brands(self, obj):
        return ", ".join([brand.name for brand in obj.applicable_brands.all()])
    get_related_brands.short_description = 'İlişkili Markalar'

    def get_related_groups(self, obj):
        return ", ".join([group.name for group in obj.applicable_groups.all()])
    get_related_groups.short_description = 'İlişkili Gruplar'

    def get_related_categories(self, obj):
        return ", ".join([category.name for category in obj.applicable_categories.all()])
    get_related_categories.short_description = 'İlişkili Kategoriler'

    def get_related_product_models(self, obj):
        return ", ".join([model.name for model in obj.applicable_product_models.all()])
    get_related_product_models.short_description = 'İlişkili Ürün Modelleri'

    # Yeni metodlar - tetikleyiciler için
    def get_melamine_triggers(self, obj):
        return ", ".join([opt.name for opt in obj.melamine_triggers.all()])
    get_melamine_triggers.short_description = 'Melamin Tetikleyicileri'

    def get_laminate_triggers(self, obj):
        return ", ".join([opt.name for opt in obj.laminate_triggers.all()])
    get_laminate_triggers.short_description = 'Laminat Tetikleyicileri'

    def get_veneer_triggers(self, obj):
        return ", ".join([opt.name for opt in obj.veneer_triggers.all()])
    get_veneer_triggers.short_description = 'Kaplama Tetikleyicileri'

    def get_lacquer_triggers(self, obj):
        return ", ".join([opt.name for opt in obj.lacquer_triggers.all()])
    get_lacquer_triggers.short_description = 'Lake Tetikleyicileri'
