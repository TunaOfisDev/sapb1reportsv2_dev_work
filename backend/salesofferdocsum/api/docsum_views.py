# backend/salesofferdocsum/api/docsum_views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models.docsum import DocumentSummary
from ..serializers import DocumentSummarySerializer
from loguru import logger

API_NAME = 'salesofferdocsum'

class DocumentSummaryListView(APIView):
    """
    Tüm belge özetlerini listeler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            summaries = DocumentSummary.objects.all()
            serializer = DocumentSummarySerializer(summaries, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.error(f"Belge özetleri listelenirken hata oluştu: {e}")
            return Response({"error": "Belge özetleri listelenirken bir hata oluştu."}, status=500)


class DocumentSummaryDocView(APIView):
    """
    Belirli bir belge numarasına göre belge özetini getirir.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, belge_no, *args, **kwargs):
        try:
            summary = DocumentSummary.objects.get(belge_no=belge_no)
            serializer = DocumentSummarySerializer(summary)
            return Response(serializer.data, status=200)
        except DocumentSummary.DoesNotExist:
            return Response({"error": "Belge özeti bulunamadı."}, status=404)
        except Exception as e:
            logger.error(f"Belge özeti getirilirken hata oluştu: {e}")
            return Response({"error": "Belge özeti getirilirken bir hata oluştu."}, status=500)
