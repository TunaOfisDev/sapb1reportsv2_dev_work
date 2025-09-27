# backend/openorderdocsum/api/docsum_views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from ..models.docsum import DocumentSummary
from ..serializers import DocumentSummarySerializer


API_NAME = 'salesorderdocsum'

class DocumentSummaryListView(APIView):
    """
    Tüm belge özetlerini listeler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cache_key = f'{API_NAME}_document_summaries'
        cached_data = cache.get(cache_key)
        if not cached_data:
            summaries = DocumentSummary.objects.all()
            serializer = DocumentSummarySerializer(summaries, many=True)
            cache.set(cache_key, serializer.data, timeout=180)  # 3 dakika cache süresi
            return Response(serializer.data)
        return Response(cached_data)


class DocumentSummaryDocView(APIView):
    """
    Belirli bir belge numarasına göre belge özetini getirir.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, belge_no, *args, **kwargs):
        cache_key = f'{API_NAME}_document_summary_{belge_no}'
        summary = cache.get(cache_key)
        if not summary:
            try:
                summary = DocumentSummary.objects.get(belge_no=belge_no)
                serializer = DocumentSummarySerializer(summary)
                cache.set(cache_key, serializer.data, timeout=30)  # 3 dakika cache süresi
                return Response(serializer.data)
            except DocumentSummary.DoesNotExist:
                return Response({"error": "Belge özeti bulunamadı."}, status=404)

        return Response(summary)

    @staticmethod
    def clear_cache_for_updated_documents(updated_belge_nos):
        # Belge numaralarına özgü önbellekleri temizle
        for belge_no in updated_belge_nos:
            cache.delete(f'{API_NAME}_document_summary_{belge_no}')
        
        # Genel önbelleği temizle
        cache.delete(f'{API_NAME}_document_summaries')
        
        

