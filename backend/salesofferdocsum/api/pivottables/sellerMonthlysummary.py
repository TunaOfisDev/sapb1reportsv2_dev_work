# backend/salesofferdocsum/api/pivottables/sellermonthlysummary.py
from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ...models.docsum import DocumentSummary
from loguru import logger

class SellerMonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_month = timezone.now().month
        current_year = timezone.now().year

        try:
            seller_monthly_summary = (
                DocumentSummary.objects
                .filter(belge_tarih__year=current_year, belge_tarih__month=current_month)
                .values('satici')
                .annotate(
                    total_net_tutar_ypb=Sum('net_tutar_ypb'),
                    total_net_tutar_spb=Sum('net_tutar_spb'),
                    total_brut_tutar_spb=Sum('brut_tutar_spb'),
                )
                .order_by('-total_net_tutar_ypb')  # Azalan sırada sıralama
            )

            return Response(seller_monthly_summary, status=200)
        except Exception as e:
            logger.error(f"Satıcı Aylık Özeti oluşturulurken hata: {e}")
            return Response({"error": "Satıcı aylık özeti oluşturulurken bir hata oluştu."}, status=500)
