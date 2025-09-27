# dosya path yolu: backend/productconfig/admin/question_option_relation.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models import QuestionOptionRelation, Option
from .resources import GenericResource


class QuestionOptionRelationResource(GenericResource):
    """
    QuestionOptionRelation modeli için Import-Export kaynağı.
    """
    class Meta:
        model = QuestionOptionRelation


@admin.register(QuestionOptionRelation)
class QuestionOptionRelationAdmin(ImportExportModelAdmin):
    """
    QuestionOptionRelation modeli için admin panel ayarları.
    """
    resource_class = QuestionOptionRelationResource

    # Zaman damgalarını sona koyarak tüm alanları sıralama
    list_display = [
        'id', 'question', 'relation_type', 'order', 'get_options', 'created_at', 'updated_at'
    ]
    list_editable = ['order']
    # Oluşturma ve güncelleme tarihlerini gizlemek için:
    exclude = ['created_at', 'updated_at']
    list_filter = ['relation_type', 'question']
    search_fields = ['question__name', 'relation_type']
    filter_horizontal = ['options']
    ordering = ['order']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        ManyToManyField görünümünü özelleştirme.
        Seçeneklerin yanında grup, kategori ve tip bilgisi gösterilir.
        """
        if db_field.name == "options":
            # İlişkili grup ve kategori bilgilerini prefetch ederek performansı artır
            kwargs["queryset"] = Option.objects.prefetch_related("applicable_groups", "applicable_categories")
            form_field = super().formfield_for_manytomany(db_field, request, **kwargs)

            # Option adlarını grup, kategori ve tip bilgisiyle birleştirerek göster
            form_field.label_from_instance = lambda obj: (
                f"{obj.name} - {', '.join([group.name for group in obj.applicable_groups.all()])} - "
                f"{', '.join([category.name for category in obj.applicable_categories.all()])} - "
                f"{obj.get_option_type_display()}"
            )
            return form_field
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        """
        Varsayılan queryset'i genişletmek için.
        """
        return super().get_queryset(request).prefetch_related('options')

    def get_options(self, obj):
        """
        ManyToManyField olan 'options' alanını gösterir.
        """
        return ", ".join([option.name for option in obj.options.all()])
    get_options.short_description = 'Options'

    def save_model(self, request, obj, form, change):
        """
        Soru ve seçenek ilişkisi kayıt işlemleri.
        """
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """
        Belirli alanları yalnızca görüntülenebilir yapmak için.
        """
        return ['id'] if obj else []

    def has_delete_permission(self, request, obj=None):
        """
        Silme izinlerini kontrol etmek için.
        """
        return True
