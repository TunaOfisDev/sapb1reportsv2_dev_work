# backend/salesofferdocsum/api/salesofferdetaildoc.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import SalesOfferDetailSerializer
from ..models.salesofferdetail import SalesOfferDetail
from django.core.cache import cache
from loguru import logger


class SalesOfferDetailDocView(APIView):
    """
    Belirli bir belge numarasına ait OpenOfferDetail detaylarını listeler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, belge_no, *args, **kwargs):
        try:
            details = SalesOfferDetail.objects.filter(belge_no=belge_no)
            if not details.exists():
                return Response({"error": "Belirtilen belge numarası ile ilgili detay bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

            serializer = SalesOfferDetailSerializer(details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Belge detayları çekerken hata oluştu: {e}")
            return Response({
                "error": "İstek işlenirken bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
