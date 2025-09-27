# backend/tunainssupplieradvancebalance/api/exportxlsx_view.py
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from import_export import resources
from import_export.fields import Field
from import_export.widgets import NumberWidget
from ..models.models import TunaInsSupplierAdvanceBalance
import tablib


class CustomNumberWidget(NumberWidget):
    def render(self, value, obj=None):
        if value is not None:
            # Decimal kullanarak kesinlik sağla ve istenen formatı uygula
            value = Decimal(value)
            # Türkiye'deki binlik ayırıcı olarak nokta ve ondalık ayırıcı olarak virgül kullanılır
            return '{:,.2f}'.format(value).replace(',', 'X').replace('.', ',').replace('X', '.')
        # Eğer değer None ise, varsayılan olarak '0,00' döndür
        return '0,00'


class TotalRiskReportResource(resources.ModelResource):
    # Tahsilat, Bakiye, Açık Teslimat, Açık Sipariş, Toplam Risk ve Avans Bakiye için field tanımlamaları

    avans_bakiye = Field(column_name='Avans Bakiye', attribute='avans_bakiye', widget=CustomNumberWidget())


    class Meta:
        model = TunaInsSupplierAdvanceBalance
        # Hangi alanların dışa aktarılacağını belirle
        fields = ('muhatap_kod', 'muhatap_ad', 'avans_bakiye')
        # Sütunları istenen sırayla belirle
        export_order = ('muhatap_kod', 'muhatap_ad',  'avans_bakiye')

    def export(self):
        # Create a new dataset with tablib
        dataset = tablib.Dataset()
        # Define headers with the fields names
        dataset.headers = self.Meta.export_order
        
        # Iterate over the queryset
        for obj in self.get_queryset():
            row = [
                getattr(obj, field) for field in self.Meta.export_order
            ]
            dataset.append(row)
        return dataset

class ExportTotalRiskXLSXView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_risk_resource = TotalRiskReportResource()
        dataset = total_risk_resource.export()
        response = HttpResponse(
            dataset.xlsx,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="total_risk_report.xlsx"'
        return response
