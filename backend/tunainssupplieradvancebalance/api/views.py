# File: backend/tunainssupplieradvancebalance/api/views.py
"""Çakışmasız TunaIns Supplier Advance Balance API views.

* Benzersiz cache anahtarı → ``TUNAIN_SUP_ADV_CACHE_KEY``
* Model: :class:`~tunainssupplieradvancebalance.models.TunaInsSupplierAdvanceBalance`
  başka uygulamalarla paylaşılmaz.
* URL ``name`` değerleri zaten benzersiz (`tunains-supplieradvance-*`).
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

from ..models.models import TunaInsSupplierAdvanceBalance
from ..permissions import HasTOTALRiskAccess
from ..serializers import TunaInsSupplierAdvanceBalanceSerializer
from ..utilities.data_fetcher import fetch_hana_db_data

logger = logging.getLogger(__name__)

# Benzersiz cache anahtarı: başka app'lerle karışmaz
TUNAIN_SUP_ADV_CACHE_KEY = "tunains_supplier_advance_reports"
CACHE_TTL = 30  # saniye


class TotalRiskListView(APIView):
    """Tedarikçi avans bakiyelerini listeler (30 s cache)."""

    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]

    def get(self, request, *args, **kwargs):
        data = cache.get(TUNAIN_SUP_ADV_CACHE_KEY)
        if data is None:
            queryset = TunaInsSupplierAdvanceBalance.objects.all()
            serializer = TunaInsSupplierAdvanceBalanceSerializer(queryset, many=True)
            data = serializer.data
            cache.set(TUNAIN_SUP_ADV_CACHE_KEY, data, CACHE_TTL)
        return Response(data)


class FetchHanaDataView(APIView):
    """SAP HANA’dan tedarikçi avans bakiyesi senkronizasyonu."""

    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2:
            return Response({"error": "Token eksik"}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]
        hana_rows = fetch_hana_db_data(token)
        if not hana_rows:
            logger.error("HANA verisi getirilemedi")
            return Response({"error": "HANA DB verisi yok"}, status=status.HTTP_502_BAD_GATEWAY)

        try:
            with transaction.atomic():
                TunaInsSupplierAdvanceBalance.objects.all().delete()
                objs = [
                    TunaInsSupplierAdvanceBalance(
                        muhatap_kod=row["TedarikciKod"],
                        muhatap_ad=row["TedarikciAd"],
                        avans_bakiye=row.get("AvansBakiye", 0),
                    )
                    for row in hana_rows
                ]
                TunaInsSupplierAdvanceBalance.objects.bulk_create(objs)

            cache.delete(TUNAIN_SUP_ADV_CACHE_KEY)
            return Response({"message": "Senkronizasyon başarılı"}, status=status.HTTP_200_OK)
        except Exception as exc:  # pragma: no cover
            logger.exception("Senkronizasyon hatası: %s", exc)
            return Response(
                {"error": "Veri güncelleme hatası", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LastUpdatedView(APIView):
    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]

    def get(self, request, *args, **kwargs):
        obj = TunaInsSupplierAdvanceBalance.objects.order_by("-updated_at").first()
        if obj:
            ts = timezone.localtime(obj.updated_at, timezone.get_fixed_timezone(180))
            return Response({"last_updated": ts.strftime("%d.%m.%Y %H:%M")})
        return Response({"last_updated": "No data"})
