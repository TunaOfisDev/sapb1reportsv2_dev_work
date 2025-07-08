# backend/deliverydocsumv2/api/dynamicnamecolumn.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from ..models.models import DeliveryDocSummary

class DynamicNameColumnView(APIView):
    """
    Dinamik kolon başlıkları döner.
    """
    def get(self, request, *args, **kwargs):
        try:
            latest_summary = DeliveryDocSummary.objects.latest('updated_at')
            now = latest_summary.updated_at

            column_names = {
                "today": f"Bugün = {now.strftime('%d.%m.%Y')}",
                "yesterday": f"Dün = {(now - timedelta(days=1)).strftime('%d.%m.%Y')}",
                "dayBeforeYesterday": f"Önceki Gün = {(now - timedelta(days=2)).strftime('%d.%m.%Y')}",
                "threeDaysAgo": f"Bugün - 3 Gün = {(now - timedelta(days=3)).strftime('%d.%m.%Y')}",
                "fourDaysAgo": f"Bugün - 4 Gün = {(now - timedelta(days=4)).strftime('%d.%m.%Y')}",
                "thisMonth": f"Bu Ay Toplam = {now.strftime('%m.%Y')}",
                "lastMonth": f"Bu Ay - 1 Toplam = {(now - relativedelta(months=1)).strftime('%m.%Y')}",
                "thisYear": f"Yıllık Toplam = {now.strftime('%Y')}"
            }

            return Response(column_names, status=status.HTTP_200_OK)
        except DeliveryDocSummary.DoesNotExist:
            return Response({"error": "Veri bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
