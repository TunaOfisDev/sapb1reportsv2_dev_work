# backend/hanadbcon/admin.py
from django.contrib import admin
from .models.sq_query_model import SQLQuery
from import_export.admin import ImportExportModelAdmin


class SQLQueryAdmin(ImportExportModelAdmin):
    """
    SQLQuery modelini yönetmek için admin paneli ayarları.
    """
    list_display = ('name', 'query_preview', 'departments_list', 'positions_list')
    search_fields = ('name', 'query')
    filter_horizontal = ('departments', 'positions')  # Many-to-Many alanlarını düzenlemek için

    def query_preview(self, obj):
        """
        Sorgunun ilk 50 karakterini gösterir.
        """
        return f"{obj.query[:50]}..." if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query Preview'

    def departments_list(self, obj):
        """
        İlgili departmanların adlarını virgülle ayırarak listeler.
        """
        return ", ".join([d.name for d in obj.departments.all()])
    departments_list.short_description = 'Departments'

    def positions_list(self, obj):
        """
        İlgili pozisyonların adlarını virgülle ayırarak listeler.
        """
        return ", ".join([p.name for p in obj.positions.all()])
    positions_list.short_description = 'Positions'


# SQLQuery modelini admin paneline kaydeder
admin.site.register(SQLQuery, SQLQueryAdmin)
