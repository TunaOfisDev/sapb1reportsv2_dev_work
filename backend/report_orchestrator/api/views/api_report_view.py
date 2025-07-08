# backend/report_orchestrator/api/views/api_report_view.py

from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from report_orchestrator.models.api_report_model import APIReportModel
from report_orchestrator.api.serializers.api_report_serializer import APIReportSerializer
from report_orchestrator.tasks.run_report import run_report

from django.http import FileResponse
from report_orchestrator.exporters.pdf_exporter import generate_pdf_from_result
from report_orchestrator.exporters.excel_exporter import generate_excel_from_result
import os

class APIReportViewSet(viewsets.ModelViewSet):
    """
    AI Center Raporlarının listelenmesi, görüntülenmesi ve güncellenmesini sağlar.
    Yeni kayıt ekleme genelde sistem tarafından yapılır.
    """
    queryset = APIReportModel.objects.all().order_by("api_name")
    serializer_class = APIReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset()

    @action(detail=False, methods=["post"], url_path="run")
    def run_single_report(self, request):
        """
        Belirtilen `api_name` değerine göre tekil bir raporu Celery ile tetikler.
        """
        api_name = request.data.get("api_name")
        if not api_name:
            return Response({"error": "api_name alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = APIReportModel.objects.get(api_name=api_name)
            run_report.delay(api_name)
            return Response({"message": f"{api_name} için Celery görevi başlatıldı."})
        except APIReportModel.DoesNotExist:
            return Response({"error": f"{api_name} isminde bir rapor bulunamadı."}, status=status.HTTP_404_NOT_FOUND)




class ReportSummaryView(APIView):
    """
    Raporun sadece özet verisini (result_json) döner.
    """
    def get(self, request, *args, **kwargs):
        report_name = request.query_params.get("name")
        if not report_name:
            return Response({"error": "Rapor ismi (name) parametresi zorunlu."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = APIReportModel.objects.get(api_name=report_name)
            if not report.result_json:
                return Response({"error": "Henüz özet veri üretilmedi."}, status=status.HTTP_404_NOT_FOUND)
            return Response(report.result_json)
        except APIReportModel.DoesNotExist:
            return Response({"error": f"{report_name} isimli rapor tanımlı değil."}, status=status.HTTP_404_NOT_FOUND)





class RunReportExportView(APIView):
    """
    Özet veriden çıktı üretir (PDF, Excel, JSON)
    /run_report/?name=...&format=pdf|xlsx|json
    """
    def get(self, request, *args, **kwargs):
        report_name = request.query_params.get("name")
        export_format = request.query_params.get("format", "json")

        if not report_name:
            return Response({"error": "Rapor ismi (name) zorunlu."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = APIReportModel.objects.get(api_name=report_name)
            data = report.result_json or {}

            if not data:
                return Response({"error": "Henüz veri üretilmedi."}, status=status.HTTP_204_NO_CONTENT)

            if export_format == "pdf":
                pdf_path = generate_pdf_from_result(report_name, data)
                return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf', filename=os.path.basename(pdf_path))

            elif export_format == "xlsx":
                xlsx_path = generate_excel_from_result(report_name, data)
                return FileResponse(open(xlsx_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=os.path.basename(xlsx_path))

            return Response(data)

        except APIReportModel.DoesNotExist:
            return Response({"error": f"{report_name} bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

