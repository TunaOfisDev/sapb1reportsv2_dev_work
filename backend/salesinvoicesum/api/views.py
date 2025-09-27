# backend/salesinvoicesum/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import SalesInvoiceSumSerializer
from ..models.sales_invoice_sum_model import SalesInvoiceSum
from ..utils.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from loguru import logger

class SalesInvoiceSumListView(APIView):
    """
    Django lokal veritabanındaki tüm SalesInvoicesum kayıtlarını listeler.
    """
    def get(self, request, *args, **kwargs):
        cached_data = cache.get('sales_invoice_summaries')
        if not cached_data:
            summaries = SalesInvoiceSum.objects.all()
            serializer = SalesInvoiceSumSerializer(summaries, many=True)
            cache.set('sales_invoice_summaries', serializer.data, timeout=30)  # 30 saniye cache süresi
            return Response(serializer.data)
        return Response(cached_data)

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
        if not token:
            return Response({
                "success": False,
                "error": "Token sağlanmadı."
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = fetch_hana_db_data(token)
            if not data:
                return Response({
                    "success": False,
                    "error": "Veri alınamadı veya boş."
                }, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                SalesInvoiceSum.objects.all().delete()
                for item in data:
                    SalesInvoiceSum.objects.create(
                        representative=item.get('Temsilci', ''),
                        customer_group=item.get('CariGrup', ''),
                        customer_code=item.get('CariKod', ''),
                        customer_name=item.get('CariAdi', ''),
                        debt_balance=item.get('BorçBakiyesi', 0),
                        advance_balance=item.get('AvansBakiyesi', 0),
                        today_total=item.get('Bugun', 0),
                        yesterday_total=item.get('Dun', 0),
                        two_days_ago_total=item.get('IkiGunOnce', 0),
                        three_days_ago_total=item.get('UcGunOnce', 0),
                        four_days_ago_total=item.get('DortGunOnce', 0),
                        weekly_total=item.get('HaftaToplam', 0),
                        monthly_total=item.get('BuAyToplam', 0),
                        last_month_total=item.get('GecenAyToplam', 0),
                        yearly_total=item.get('BuYilToplam', 0),
                        open_orders_total=item.get('AcikSiparisToplami', 0),
                        open_shipments_total=item.get('AcikSevkiyatToplami', 0),
                        invoice_count=item.get('FaturaSayisi', 0),
                    )

            cache.delete('sales_invoice_summaries')
            return Response({
                "success": True,
                "message": "HANA DB verileri başarıyla güncellendi ve cache temizlendi."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"HANA verileri çekerken hata oluştu: {e}")
            return Response({
                "success": False,
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
