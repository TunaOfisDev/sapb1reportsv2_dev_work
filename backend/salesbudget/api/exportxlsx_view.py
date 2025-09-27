# backend/salesbudget/api/resources.py
from import_export import resources
from import_export.fields import Field
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from salesbudget.models.models import SalesBudget

class CustomDecimalField(Field):
    def get_value(self, obj):
        value = super().get_value(obj)
        if value is None:
            return ""
        return str(value).replace('.', ',')

class SalesBudgetResource(resources.ModelResource):
    toplam_gercek = CustomDecimalField(column_name='Toplam Gerçek', attribute='toplam_gercek')
    toplam_hedef = CustomDecimalField(column_name='Toplam Hedef', attribute='toplam_hedef')
    yuzde_oran = CustomDecimalField(column_name='Oran', attribute='yuzde_oran_hesapla')
    oca_gercek = CustomDecimalField(column_name='Oca Gerçek', attribute='oca_gercek')
    oca_hedef = CustomDecimalField(column_name='Oca Hedef', attribute='oca_hedef')
    sub_gercek = CustomDecimalField(column_name='Sub Gerçek', attribute='sub_gercek')
    sub_hedef = CustomDecimalField(column_name='Sub Hedef', attribute='sub_hedef')
    mar_gercek = CustomDecimalField(column_name='Mar Gerçek', attribute='mar_gercek')
    mar_hedef = CustomDecimalField(column_name='Mar Hedef', attribute='mar_hedef')
    nis_gercek = CustomDecimalField(column_name='Nis Gerçek', attribute='nis_gercek')
    nis_hedef = CustomDecimalField(column_name='Nis Hedef', attribute='nis_hedef')
    may_gercek = CustomDecimalField(column_name='May Gerçek', attribute='may_gercek')
    may_hedef = CustomDecimalField(column_name='May Hedef', attribute='may_hedef')
    haz_gercek = CustomDecimalField(column_name='Haz Gerçek', attribute='haz_gercek')
    haz_hedef = CustomDecimalField(column_name='Haz Hedef', attribute='haz_hedef')
    tem_gercek = CustomDecimalField(column_name='Tem Gerçek', attribute='tem_gercek')
    tem_hedef = CustomDecimalField(column_name='Tem Hedef', attribute='tem_hedef')
    agu_gercek = CustomDecimalField(column_name='Agu Gerçek', attribute='agu_gercek')
    agu_hedef = CustomDecimalField(column_name='Agu Hedef', attribute='agu_hedef')
    eyl_gercek = CustomDecimalField(column_name='Eyl Gerçek', attribute='eyl_gercek')
    eyl_hedef = CustomDecimalField(column_name='Eyl Hedef', attribute='eyl_hedef')
    eki_gercek = CustomDecimalField(column_name='Eki Gerçek', attribute='eki_gercek')
    eki_hedef = CustomDecimalField(column_name='Eki Hedef', attribute='eki_hedef')
    kas_gercek = CustomDecimalField(column_name='Kas Gerçek', attribute='kas_gercek')
    kas_hedef = CustomDecimalField(column_name='Kas Hedef', attribute='kas_hedef')
    ara_gercek = CustomDecimalField(column_name='Ara Gerçek', attribute='ara_gercek')
    ara_hedef = CustomDecimalField(column_name='Ara Hedef', attribute='ara_hedef')

    class Meta:
        model = SalesBudget
        fields = ('satici', 'toplam_gercek', 'toplam_hedef','yuzde_oran', 'oca_gercek', 'oca_hedef',
                  'sub_gercek', 'sub_hedef','mar_gercek', 'mar_hedef','nis_gercek', 'nis_hedef',
                  'may_gercek', 'may_hedef','haz_gercek', 'haz_hedef','tem_gercek', 'tem_hedef',
                  'agu_gercek', 'agu_hedef','eyl_gercek', 'eyl_hedef','eki_gercek', 'eki_hedef',
                  'kas_gercek', 'kas_hedef','ara_gercek', 'ara_hedef') # Burada diğer tüm fieldlarınızı ekleyin
        export_order = fields # İsteğe bağlı olarak dışa aktarma sırasını burada belirleyebilirsiniz.


class ExportSalesBudgetXLSXView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sales_budget_resource = SalesBudgetResource()
        dataset = sales_budget_resource.export()
        response = HttpResponse(
            dataset.xlsx,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="sales_budget_{request.user.email}.xlsx"'
        return response

