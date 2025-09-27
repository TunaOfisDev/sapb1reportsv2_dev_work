# backend/tunainssupplieradvancebalance/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models.models import TunaInsSupplierAdvanceBalance

class TotalRiskReportResource(resources.ModelResource):
    class Meta:
        model = TunaInsSupplierAdvanceBalance
        # fields attribute ile hangi alanların içeri/dışarı aktarılacağını belirleyebilirsiniz.
        # skip_unchanged attribute ile değişmeyen kayıtların atlanmasını sağlayabilirsiniz.
        # report_skipped attribute ile atlanan kayıtların rapor edilmesini sağlayabilirsiniz.
        # import_id_fields attribute ile hangi alanın ID olarak kullanılacağını belirleyebilirsiniz.
        fields = ('muhatap_kod', 'muhatap_ad', 'avans_bakiye')
        export_order = fields
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['muhatap_kod']

class TunaInsSupplierAdvanceBalanceAdmin(ImportExportModelAdmin):
    resource_class = TotalRiskReportResource
    list_display = ('muhatap_ad', 'muhatap_kod', 'avans_bakiye', 'created_at', 'updated_at')
    list_filter = ('muhatap_kod', 'muhatap_ad')
    search_fields = ('muhatap_ad', 'muhatap_kod')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(TunaInsSupplierAdvanceBalance, TunaInsSupplierAdvanceBalanceAdmin)

