# backend/salesorder/api/exportxlsx_view.py
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from import_export.widgets import NumberWidget
from ..serializers import CustomerSalesOrderResource

class CustomNumberWidget(NumberWidget):
    def render(self, value, obj=None):
        return format(value, '.2f').replace('.', ',')


class ExportXLSXView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer_sales_order_resource = CustomerSalesOrderResource()
        dataset = customer_sales_order_resource.export()
        xlsx_data = dataset.export('xlsx')
        response = HttpResponse(
            xlsx_data, 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="customer_sales_orders.xlsx"'
        return response
