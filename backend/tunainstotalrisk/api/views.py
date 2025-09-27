# File: backend/tunainstotalrisk/api/views.py

"""Isolated API views for TunaIns TotalRisk.

* Kullanılan model: :class:`~tunainstotalrisk.models.TunainsTotalRiskReport`
* Cache key'leri, `totalrisk` uygulamasıyla kesinlikle çakışmaması için benzersizleştirildi.
"""

import logging
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.models import TunainsTotalRiskReport
from ..permissions import HasTOTALRiskAccess
from ..serializers import TunainsTotalRiskReportSerializer
from ..utilities.data_fetcher import fetch_hana_db_data

logger = logging.getLogger(__name__)

# Benzersiz cache key – diğer modüllerle çakışmaz
CACHE_KEY = "tunains_total_risk_reports"
CACHE_TIMEOUT = 30  # saniye


class TunainsTotalRiskListView(APIView):
    """TunaIns TotalRisk raporlarını listeler (30 s cache)."""

    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]

    def get(self, request, *args, **kwargs):
        data = cache.get(CACHE_KEY)
        if data is None:
            qs = TunainsTotalRiskReport.objects.all()
            serializer = TunainsTotalRiskReportSerializer(qs, many=True)
            data = serializer.data
            cache.set(CACHE_KEY, data, CACHE_TIMEOUT)
        return Response(data)


class FetchHanaDataView(APIView):
    """HANA DB'den veri çekip `TunainsTotalRiskReport` tablosunu tazeler."""

    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2:
            return Response({"error": "Bearer token eksik"}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]
        hana_data = fetch_hana_db_data(token)
        if not hana_data:
            logger.error("[TunaInsTotalRisk] HANA verisi boş döndü")
            return Response({"error": "HANA verisi alınamadı"}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            with transaction.atomic():
                TunainsTotalRiskReport.objects.all().delete()
                bulk_objs = [
                    TunainsTotalRiskReport(
                        muhatap_kod=row["MuhatapKod"],
                        satici=row.get("Satici"),
                        grup=row.get("Grup"),
                        avans_kod=row["AvansKod"],
                        muhatap_ad=row["MuhatapAd"],
                        bakiye=row["Bakiye"],
                        acik_teslimat=row["AcikTeslimat"],
                        acik_siparis=row["AcikSiparis"],
                        avans_bakiye=row.get("AvansBakiye", 0),
                        toplam_risk=row["ToplamRisk"],
                    )
                    for row in hana_data
                ]
                TunainsTotalRiskReport.objects.bulk_create(bulk_objs, batch_size=1000)
        except Exception as exc:  # pragma: no cover
            logger.exception("[TunaInsTotalRisk] Veri güncelleme hatası: %s", exc)
            return Response({"error": "DB update failed", "details": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        cache.delete(CACHE_KEY)
        return Response({"message": "Veri güncellendi"}, status=status.HTTP_200_OK)


class LastUpdatedView(APIView):
    """Son güncelleme zamanını döndürür."""

    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]

    def get(self, request, *args, **kwargs):
        latest = TunainsTotalRiskReport.objects.order_by("-updated_at").first()
        if not latest:
            return Response({"last_updated": "N/A"})
        ts = timezone.localtime(latest.updated_at, timezone=timezone.get_fixed_timezone(180))
        return Response({"last_updated": ts.strftime("%d.%m.%Y %H:%M")})
