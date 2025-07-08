# backend/openorderdocsum/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import SalesOrderDetailSerializer
from ..models.salesorderdetail import SalesOrderDetail
from loguru import logger


class SalesOrderDetailDocView(APIView):
    """
    Belirli bir belge numarasına ait OpenOrderDetail detaylarını listeler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, belge_no, *args, **kwargs):
        try:
            details = SalesOrderDetail.objects.filter(belge_no=belge_no)
            if not details.exists():
                return Response({"error": "Belirtilen belge numarası ile ilgili detay bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

            serializer = SalesOrderDetailSerializer(details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Belge detayları çekerken hata oluştu: {e}")
            return Response({
                "error": "İstek işlenirken bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
