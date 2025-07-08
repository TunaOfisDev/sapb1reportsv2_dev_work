# backend/openorderdocsum/api/docsum_views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from ..models.docsum import DocumentSummary
from ..serializers import DocumentSummarySerializer
from loguru import logger

class DocumentSummaryListView(APIView):
    """
    Tüm belge özetlerini listeler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cached_data = cache.get('document_summaries')
        if not cached_data:
            summaries = DocumentSummary.objects.all()
            serializer = DocumentSummarySerializer(summaries, many=True)
            cache.set('document_summaries', serializer.data, timeout=10)  # 60 saniye cache süresi
            return Response(serializer.data)
        return Response(cached_data)

class DocumentSummaryDocView(APIView):
    """
    Belirli bir belge numarasına göre belge özetini getirir.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, belge_no, *args, **kwargs):
        summary = cache.get(f'document_summary_{belge_no}')
        if not summary:
            try:
                summary = DocumentSummary.objects.get(belge_no=belge_no)
                serializer = DocumentSummarySerializer(summary)
                cache.set(f'document_summary_{belge_no}', serializer.data, timeout=60)  # 60 saniye cache süresi
                return Response(serializer.data)
            except DocumentSummary.DoesNotExist:
                return Response({"error": "Belge özeti bulunamadı."}, status=404)

        return Response(summary)
