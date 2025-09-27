# backend/salesbudgeteur/api/export_excel.py

from rest_framework.views import APIView
from rest_framework import permissions
from django.http import HttpResponse
from tablib import Dataset
from salesbudgeteur.models.salesbudget_model import SalesBudgetEURModel

class ExportSalesBudgetEURXLSXView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        dataset = Dataset()
        month_keys = ['oca', 'sub', 'mar', 'nis', 'may', 'haz', 'tem', 'agu', 'eyl', 'eki', 'kas', 'ara']

        headers = [
            "Satıcı", "Yıl",
            "Toplam Gerçek EUR", "Toplam Hedef EUR", "Yıllık Oran (%)",
            "Toplam İptal EUR", "Toplam Elle Kapanan EUR",
            "Kapalı Sipariş Listesi"
        ]

        for m in month_keys:
            headers.append(f"{m.upper()} Gerçek")
            headers.append(f"{m.upper()} Hedef")
            headers.append(f"{m.upper()} Oran (%)")

        dataset.headers = headers

        # 🔍 Prefetch yapılmazsa aylık veriler boş olur
        for item in SalesBudgetEURModel.objects.prefetch_related("aylik_veriler").all():
            aylik_map = {v.ay: v for v in item.aylik_veriler.all()}

            row = [
                item.satici,
                item.yil,
                item.toplam_gercek_eur,
                item.toplam_hedef_eur,
                round((item.toplam_gercek_eur or 0) / (item.toplam_hedef_eur or 1) * 100, 2),
                item.toplam_iptal_eur,
                item.toplam_elle_kapanan_eur,
                item.kapali_sip_list or "",
            ]

            for i, key in enumerate(month_keys, 1):
                veri = aylik_map.get(i)
                g = veri.gercek_tutar if veri else 0
                h = veri.hedef_tutar if veri else 0
                oran = round((g / h * 100), 2) if h else 0
                row.extend([g, h, oran])

            dataset.append(row)

        response = HttpResponse(
            dataset.export("xlsx"),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=salesbudget-eur-full.xlsx"
        return response
