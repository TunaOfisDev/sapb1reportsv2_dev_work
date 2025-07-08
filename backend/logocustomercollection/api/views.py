# backend/logocustomercollection/api/views.py

from datetime import datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..tasks import save_raw_transactions, generate_aging_summaries
from ..serializers import LogoCustomerCollectionAgingSummarySerializer
from ..models.closinginvoice import LogoCustomerCollectionAgingSummary
from ..models.models import LogoCustomerCollectionTransaction
from django.db.models import Max
from datetime import datetime, timezone

class FetchLogoDataView(APIView):
    """
    Logo DB'den API üstünden ham veriyi çeker ve yaşlandırma özet tablosunu yeniden oluşturur.
    Endpoint: /api/v2/logocustomercollection/fetch-hana-data/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return Response(
                {"error": "Token eksik veya geçersiz."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # Ham tabloyu ve özet tabloyu sıfırla
            LogoCustomerCollectionTransaction.objects.all().delete()
            LogoCustomerCollectionAgingSummary.objects.all().delete()

            # Celery görevleri senkron şekilde çağrılıyor
            raw_result = save_raw_transactions(token)
            summary_result = generate_aging_summaries()

            return Response({
                "status": "success",
                "message": f"{raw_result} | {summary_result}",
                "lastUpdated": datetime.now().strftime("%d-%m-%Y %H:%M"),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Veri çekme veya analiz sırasında hata oluştu: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerAgingSummaryView(APIView):
    """
    Yaşlandırma özet verisini JSON olarak döner.
    Endpoint: /api/v2/logocustomercollection/summary/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = LogoCustomerCollectionAgingSummary.objects.all().order_by("cari_kod")
        serializer = LogoCustomerCollectionAgingSummarySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LastUpdatedView(APIView):
    """
    En son oluşturulan / güncellenen özet kaydın tam zaman damgasını
    ve mevcut sunucu saatini döndürür.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = LogoCustomerCollectionAgingSummary.objects.aggregate(
            last_updated=Max("updated_at")
        )["last_updated"]

        return Response(
            {
                # ISO-8601 formatıyla dön; frontend isterse parse edip locale’e çevirir
                "lastUpdated": latest.isoformat() if latest else None,
                "serverTime": datetime.now(timezone.utc).astimezone().isoformat(),
                "timezone": "TRT (UTC+3)",
            },
            status=status.HTTP_200_OK,
        )