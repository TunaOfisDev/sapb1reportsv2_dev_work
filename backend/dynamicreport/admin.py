# backend\dynamicreport\admin.py
from django.contrib import admin
from django.db import DatabaseError
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models.models import SqlQuery, DynamicTable, DynamicHeaders, HanaDataType
from .utilities.hana_services import execute_hana_sql_query

class SqlQueryResource(resources.ModelResource):
    class Meta:
        model = SqlQuery
        fields = ('table_name', 'query', 'description', 'created_at')
        import_id_fields = ('table_name',)

class SqlQueryAdmin(ImportExportModelAdmin):
    list_display = ('table_name', 'created_at', )
    search_fields = ('table_name', 'description', 'created_at')
    list_filter = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('table_name', 'query','description')
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at',)
    actions = ['test_and_generate_report']

    resource_class = SqlQueryResource

    def test_and_generate_report(self, request, queryset):
        for sql_query in queryset:
            try:
                # SQL sorgusunu çalıştır ve HANA'dan verileri al
                result = execute_hana_sql_query(sql_query.query, sql_query.table_name)
                self.message_user(request, f'SQL sorgusu "{sql_query.table_name}" başarıyla çalıştırıldı ve dinamik rapor oluşturuldu.', level='success')
            except DatabaseError as e:
                self.message_user(request, 'HANA servisi çalışmıyor. Lütfen HANA servisini başlatın.', level='error')
            except Exception as e:
                self.message_user(request, f'Genel bir hata meydana geldi: {str(e)}', level='error')


    test_and_generate_report.short_description = "Seçilen SQL sorgularını test et ve dinamik rapor oluştur"

admin.site.register(SqlQuery, SqlQueryAdmin)

class DynamicTableAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'hana_data_set','fetched_at')
    search_fields = ('table_name', 'hana_data_set')
    list_filter = ('table_name', 'hana_data_set')
    fieldsets = (
        (None, {
            'fields': ('table_name', 'hana_data_set', 'sql_query', 'fetched_at')
        }),
    )

admin.site.register(DynamicTable, DynamicTableAdmin)

class DynamicHeadersAdmin(admin.ModelAdmin):
    list_display = ('table_name','dynamic_table', 'line_no', 'header_name', 'type')
    search_fields = ('table_name', 'header_name')
    list_filter = ('table_name', 'line_no')
    fieldsets = (
        (None, {
            'fields': ('table_name', 'line_no', 'header_name', 'type', 'dynamic_table')
        }),
    )

    def save(self, *args, **kwargs):
        sql_query_instance, created = SqlQuery.objects.get_or_create(table_name=self.table_name)
        dynamic_table, created = DynamicTable.objects.get_or_create(
            table_name=self.table_name, 
            sql_query=sql_query_instance  # Burada SqlQuery nesnesini ilişkilendiriyoruz
        )
        self.dynamic_table = dynamic_table
        super(DynamicHeaders, self).save(*args, **kwargs)


admin.site.register(DynamicHeaders, DynamicHeadersAdmin)

class HanaDataTypeResource(resources.ModelResource):
    class Meta:
        model = HanaDataType
        fields = ('type_code', 'type_class', 'formatter_function_name', 'type_description')
        import_id_fields = ('type_code',)
class HanaDataTypeAdmin(ImportExportModelAdmin):
    list_display = ('type_code', 'type_class', 'formatter_function_name', 'type_description')
    resource_class = HanaDataTypeResource

admin.site.register(HanaDataType, HanaDataTypeAdmin)