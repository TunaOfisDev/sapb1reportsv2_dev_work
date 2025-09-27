# File: backend/activities/api/views.py

import logging
from datetime import timedelta
from django.core.cache import cache
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from import_export.formats.base_formats import XLSX
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from tablib import Dataset

from ..models.models import Activity
from ..serializers import ActivitySerializer
from ..utilities.data_fetcher import fetch_hana_db_data
from ..utilities.parsers import parse_date, parse_time, parse_datetime

logger = logging.getLogger(__name__)


class APIRootView(APIView):
    """Return the list of available endpoints for the Activities API."""

    def get(self, request, format=None):
        api_urls = {
            "Activities List": request.build_absolute_uri(
                reverse("activities:activity-list")
            ),
            "Fetch HANA Data": request.build_absolute_uri(
                reverse("activities:fetch-hana-activities")
            ),
        }
        return Response(api_urls)


class ActivityListView(APIView):
    """List all activities – cached for 30 s to avoid hammering the DB."""

    permission_classes = [IsAuthenticated]
    CACHE_KEY = "activities_list"
    CACHE_TTL = 30  # seconds

    def get(self, request, format=None):
        try:
            activities_data = cache.get(self.CACHE_KEY)
            if activities_data is None:
                queryset = Activity.objects.all()
                serializer = ActivitySerializer(queryset, many=True)
                activities_data = serializer.data
                cache.set(self.CACHE_KEY, activities_data, self.CACHE_TTL)

            return Response(activities_data)
        except Exception as exc:  # pragma: no cover
            logger.exception("Unable to list activities: %s", exc)
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FetchHanaDataView(APIView):
    """
    Synchronise CRM activities from the SAP HANA DB into Django.

    - Pulls fresh data via `fetch_hana_db_data`.
    - Deletes Django activities that disappeared from HANA.
    - Prunes activities older than 10 days to keep the table lean.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2:
            return Response(
                {"error": "Authorization token missing"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = parts[1]
        hana_data = fetch_hana_db_data(token)
        if not hana_data:
            logger.error("Failed to fetch data from HANA DB")
            return Response(
                {"error": "Failed to fetch data from HANA DB"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        hana_numbers = [row["Numara"] for row in hana_data]

        # Remove activities that were deleted in HANA
        Activity.objects.exclude(numara__in=hana_numbers).delete()

        # Prune records older than 10 days (business rule)
        ten_days_ago = timezone.now() - timedelta(days=10)
        Activity.objects.filter(baslangic_tarihi__lt=ten_days_ago).delete()

        for row in hana_data:
            Activity.objects.update_or_create(
                numara=row["Numara"],
                defaults={
                    # YENİ alan
                    "create_datetime": parse_datetime(row["create_datetime"]),

                    "baslangic_tarihi": parse_date(row["BaslangicTarihi"]),
                    "bitis_tarihi":     parse_date(row.get("BitisTarihi")),
                    "baslama_saati":    parse_time(row.get("BaslamaSaati")),
                    "bitis_saati":      parse_time(row.get("BitisSaati")),
                    "sure":             row.get("Sure") or "-",
                    "isleyen":          row["Isleyen"],
                    "tayin_eden":       row["TayinEden"],
                    "aktivite":         row.get("Aktivite")     or "-",
                    "tur":              row.get("Tur")          or "-",
                    "konu":             row.get("Konu")         or "-",
                    "muhatap_kod":      row.get("MuhatapKod")   or "-",
                    "muhatap_ad":       row.get("MuhatapAd")    or "-",
                    "durum":            row.get("Durum")        or "-",
                    "aciklama":         row.get("Aciklama")     or "-",
                    "icerik":           row.get("Icerik")       or "-",
                },
            )

        cache.delete(ActivityListView.CACHE_KEY)  # bust list cache after sync
        return Response(
            {"message": "CRM activities successfully synchronised"},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Utility view: export activities to XLSX
# ---------------------------------------------------------------------------


def export_activities_xlsx(request):
    queryset = Activity.objects.all().values(
        "baslangic_tarihi",
        "isleyen",
        "aciklama",
        "icerik",
    )

    dataset = Dataset(headers=["Başlangıç Tarihi", "İşleyen", "Açıklama ve İçerik"])
    for activity in queryset:
        start_date = activity["baslangic_tarihi"]
        actor = activity["isleyen"]
        description = f"{activity['aciklama'] or ''} {activity['icerik'] or ''}".strip()
        dataset.append([start_date, actor, description])

    response = HttpResponse(
        dataset.export(format=XLSX),
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = 'attachment; filename="activities.xlsx"'
    return response
