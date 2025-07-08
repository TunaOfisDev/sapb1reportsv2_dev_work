# backend/report_orchestrator/api/views/sofitel_balance_report_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from report_orchestrator.models.api_report_model import APIReportModel

class SofitelBalanceReportView(APIView):
    """
    Sofitel özel raporu – sadece özet (summary) veriyi döner.
    Artık tetikleme içermez, pasif yapıdadır.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            report = APIReportModel.objects.get(api_name="sofitel_balance_report")
            if not report.result_json:
                return Response({"message": "Henüz veri yok."}, status=status.HTTP_204_NO_CONTENT)
            return Response(report.result_json)
        except APIReportModel.DoesNotExist:
            return Response({"error": "Rapor tanımı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
