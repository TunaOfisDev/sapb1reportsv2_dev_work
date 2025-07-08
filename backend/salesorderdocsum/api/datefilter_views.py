# backend/openorderdocsum/api/datefilter_views.py

from rest_framework import views, status
from rest_framework.response import Response
from ..models.docsum import DocumentSummary
from ..serializers import DocumentSummarySerializer

class DateFilterView(views.APIView):
    """
    Belge tarihine ve teslim tarihine göre belge özetlerini filtreleyen API view.
    """
    def get(self, request, *args, **kwargs):
        belge_tarih_start = request.query_params.get('belge_tarih_start')
        belge_tarih_end = request.query_params.get('belge_tarih_end')
        teslim_tarih_start = request.query_params.get('teslim_tarih_start')
        teslim_tarih_end = request.query_params.get('teslim_tarih_end')

        if belge_tarih_start and belge_tarih_end:
            documents = DocumentSummary.objects.filter(
                belge_tarih__range=[belge_tarih_start, belge_tarih_end]
            )
        elif teslim_tarih_start and teslim_tarih_end:
            documents = DocumentSummary.objects.filter(
                teslim_tarih__range=[teslim_tarih_start, teslim_tarih_end]
            )
        else:
            return Response({
                'error': 'Invalid date parameters'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = DocumentSummarySerializer(documents, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # POST isteklerini işleme
        serializer = DocumentSummarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
