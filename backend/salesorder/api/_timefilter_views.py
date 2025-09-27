# backend/salesorder/api/timefilter_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models.models import SalesOrder
from ..serializers import SalesOrderSerializer
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

class SalesOrderTimeFilteredView(APIView):
    """
    Zaman filtresine göre SalesOrder kayıtlarını listeler.
    """

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('startdate')
        end_date = request.query_params.get('enddate')

        # Kullanıcı tarafından belirtilen tarihleri ayrıştır
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        if start_date and end_date:
            # Kullanıcı tarafından belirtilen tarih aralığına göre filtrele
            filtered_sales_orders = SalesOrder.objects.filter(
                belge_tarihi__gte=start_date, belge_tarihi__lte=end_date)
        else:
            # Önceden tanımlı zaman filtrelerini kullan
            time_filter = request.query_params.get('time_filter', 'daily')
            current_time = datetime.now()

            if time_filter == 'daily':
                start_time = current_time - timedelta(days=1)
            elif time_filter == 'weekly':
                start_time = current_time - timedelta(weeks=1)
            elif time_filter == 'monthly':
                start_time = current_time - timedelta(days=30)
            elif time_filter == 'quarterly':
                start_time = current_time - timedelta(days=90)
            elif time_filter == 'yearly':
                start_time = current_time - timedelta(days=365)
            else:
                return Response({"error": "Geçersiz zaman filtresi."}, status=400)

            filtered_sales_orders = SalesOrder.objects.filter(belge_tarihi__gte=start_time)

        serializer = SalesOrderSerializer(filtered_sales_orders, many=True)
        return Response(serializer.data)
