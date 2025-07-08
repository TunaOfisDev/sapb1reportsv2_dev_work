# backend/rawmaterialwarehousestock/api/export_views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models.models import RawMaterialWarehouseStock
from django.utils.timezone import make_naive, is_aware
from datetime import datetime
from django.http import HttpResponse
from openpyxl import Workbook
import io

class ColumnFilterExportView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        column_filters = request.data.get('column_filters', {})
        
        queryset = RawMaterialWarehouseStock.objects.all()
        
        # Filtreleri uygula
        for field, value in column_filters.items():
            if field in [f.name for f in RawMaterialWarehouseStock._meta.fields]:
                try:
                    value = float(value)
                    queryset = queryset.filter(**{f"{field}__icontains": value})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__icontains": value})

        return self.export_data(queryset)

    def export_data(self, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = "Hammadde Depo Stok"

        # Başlığı yaz
        header = [field.name for field in RawMaterialWarehouseStock._meta.fields]
        ws.append(header)

        # Verileri yaz
        for obj in queryset:
            row = []
            for field in header:
                value = getattr(obj, field)
                if isinstance(value, datetime):
                    if is_aware(value):
                        value = make_naive(value)
                row.append(value)
            ws.append(row)

        # Sütun genişliklerini ayarla
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        # Excel dosyasını oluştur
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=hammadde_depo_stok_filtreli.xlsx'
        return response

