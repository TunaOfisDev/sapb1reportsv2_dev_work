# backend/logodbcon/admin.py
from django.contrib import admin
from .models.sq_query_model import SQLQuery
from import_export.admin import ImportExportModelAdmin


class SQLQueryAdmin(ImportExportModelAdmin):
    list_display = ('name', 'query_preview', 'departments_list', 'positions_list')
    search_fields = ('name', 'query')
    filter_horizontal = ('departments', 'positions')

    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query Preview'

    def departments_list(self, obj):
        return ", ".join([d.name for d in obj.departments.all()])
    departments_list.short_description = 'Departments'

    def positions_list(self, obj):
        return ", ".join([p.name for p in obj.positions.all()])
    positions_list.short_description = 'Positions'

admin.site.register(SQLQuery, SQLQueryAdmin)

