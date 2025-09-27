# dosya path yolu: backend/productconfig/admin/base.py
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .resources import GenericResource

class GenericAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    """
    Ortak admin ayarları.
    """
    exclude = ('created_at', 'updated_at')
    ordering = ('id',)
    resource_class = GenericResource

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        if not hasattr(self, 'list_display'):
            self.list_display = [
                field.name for field in model._meta.fields 
                if field.name not in ('created_at', 'updated_at', 'image')
            ]
        self.search_fields = [
            field.name for field in model._meta.fields 
            if field.get_internal_type() == 'CharField' and hasattr(model, field.name)
        ]
        self.resource_class = type(
            f"{model.__name__}Resource",
            (GenericResource,),
            {'Meta': type('Meta', (), {'model': model})}
        )
