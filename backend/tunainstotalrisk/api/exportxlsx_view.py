# backend/tunainstotalrisk/api/exportxlsx_view.py
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from import_export import resources
from import_export.fields import Field
from import_export.widgets import NumberWidget
from ..models.models import TunainsTotalRiskReport
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


class TunainsTotalRiskReportResource(resources.ModelResource):
    # Tahsilat, Bakiye, Açık Teslimat, Açık Sipariş, Toplam Risk ve Avans Bakiye için field tanımlamaları
    bakiye = Field(column_name='Bakiye', attribute='bakiye', widget=CustomNumberWidget())
    acik_teslimat = Field(column_name='Açık Teslimat', attribute='acik_teslimat', widget=CustomNumberWidget())
    acik_siparis = Field(column_name='Açık Sipariş', attribute='acik_siparis', widget=CustomNumberWidget())
    avans_bakiye = Field(column_name='Avans Bakiye', attribute='avans_bakiye', widget=CustomNumberWidget())
    toplam_risk = Field(column_name='Toplam Risk', attribute='toplam_risk', widget=CustomNumberWidget())

    class Meta:
        model = TunainsTotalRiskReport
        # Hangi alanların dışa aktarılacağını belirle
        fields = ('satici', 'grup', 'muhatap_kod', 'muhatap_ad', 'bakiye', 'acik_teslimat', 'acik_siparis', 'avans_bakiye', 'toplam_risk')
        # Sütunları istenen sırayla belirle
        export_order = ('satici', 'grup', 'muhatap_kod', 'muhatap_ad', 'bakiye', 'acik_teslimat', 'acik_siparis', 'avans_bakiye', 'toplam_risk')

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

class ExportTunainsTotalRiskXLSXView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_risk_resource = TunainsTotalRiskReportResource()
        dataset = total_risk_resource.export()
        response = HttpResponse(
            dataset.xlsx,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="total_risk_report.xlsx"'
        return response
