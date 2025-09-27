# backend/salesinvoicesum/api/dynamicnamecolumn.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from ..models.sales_invoice_sum_model import SalesInvoiceSum

class DynamicNameColumnView(APIView):
    """
    Dinamik kolon başlıkları döner.
    """
    def get(self, request, *args, **kwargs):
        try:
            latest_summary = SalesInvoiceSum.objects.latest('updated_at')
            now = latest_summary.updated_at
            column_names = {
                "today": f"{now.strftime('%d.%m')}",
                "yesterday": f"{(now - timedelta(days=1)).strftime('%d.%m')}",
                "dayBeforeYesterday": f"{(now - timedelta(days=2)).strftime('%d.%m')}",
                "threeDaysAgo": f"{(now - timedelta(days=3)).strftime('%d.%m')}",
                "fourDaysAgo": f"{(now - timedelta(days=4)).strftime('%d.%m')}",
                "weeklyTotal": f"Hafta={(now - timedelta(days=6)).strftime('%d.%m.%Y')} - {now.strftime('%d.%m.%Y')}",
                "thisMonth": f"Bu Ay={now.strftime('%m.%Y')}",
                "lastMonth": f"Geçen Ay={(now - relativedelta(months=1)).strftime('%m.%Y')}",
                "thisYear": f"{now.strftime('%Y')}"
            }
            return Response(column_names, status=status.HTTP_200_OK)
        except SalesInvoiceSum.DoesNotExist:
            return Response({"error": "Veri bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)