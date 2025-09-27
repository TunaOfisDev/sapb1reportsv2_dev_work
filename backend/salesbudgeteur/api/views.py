# backend/salesbudgeteur/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models.salesbudget_model import SalesBudgetEURModel, MonthlySalesBudgetEUR
from ..api.serializers import SalesBudgetEURSerializer
from ..utils.data_fetcher import fetch_hana_db_data


class SalesBudgetEURListView(APIView):
    """
    ✅ Local DB'den Satış Bütçesi – EUR verilerini getirir.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = SalesBudgetEURModel.objects.prefetch_related("aylik_veriler").all()
        serializer = SalesBudgetEURSerializer(queryset, many=True)
        return Response(serializer.data)


class FetchHanaSalesBudgetEURView(APIView):
    """
    ✅ SAP HANA'dan canlı veri çekip local DB'ye kaydeder.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return Response({"error": "Token eksik"}, status=status.HTTP_401_UNAUTHORIZED)

        data = fetch_hana_db_data(token)
        if data is None:
            return Response({"error": "Veri alınamadı"}, status=status.HTTP_502_BAD_GATEWAY)

        SalesBudgetEURModel.objects.all().delete()

        for row in data:
            parent = SalesBudgetEURModel.objects.create(
                satici=row.get("Satici") or "Bilinmeyen",
                yil=2025,
                toplam_gercek_eur=_safe_decimal(row.get("Toplam_Gercek_EUR")),
                toplam_hedef_eur=_safe_decimal(row.get("Toplam_Hedef_EUR")),
                toplam_iptal_eur=_safe_decimal(row.get("Toplam_Iptal_EUR")),
                toplam_elle_kapanan_eur=_safe_decimal(row.get("Toplam_Elle_Kapanan_EUR")),
                kapali_sip_list=row.get("Kapali_Sip_List", ""),
            )
            for ay in range(1, 13):
                MonthlySalesBudgetEUR.objects.create(
                    parent=parent,
                    ay=ay,
                    gercek_tutar=_safe_decimal(row.get(f"{_ay_ad(ay)}_Gercek")),
                    hedef_tutar=_safe_decimal(row.get(f"{_ay_ad(ay)}_Hedef")),
                )

        return Response({"message": "HANA verisi başarıyla içe aktarıldı."}, status=status.HTTP_201_CREATED)


def _safe_decimal(value):
    """
    Hatalı, boş, null veya parse edilemeyen değerleri güvenli şekilde 0.0 olarak döner.
    """
    if value in (None, '', 'null', 'NULL'):
        return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0



def _ay_ad(ay: int) -> str:
    adlar = [
        "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
    ]
    return adlar[ay - 1]
