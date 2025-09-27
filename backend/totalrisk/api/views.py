# backend/totalrisk/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from ..serializers import TotalRiskReportSerializer
from ..models.models import TotalRiskReport
from ..utilities.data_fetcher import fetch_hana_db_data
from django.core.cache import cache
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..permissions import HasTOTALRiskAccess  # HasTOTALRiskAccess yetkisini ekledik

class TotalRiskListView(APIView):
    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]  # Yetkilendirme ayarları eklendi

    def get(self, request, *args, **kwargs):
        cached_data = cache.get('total_risk_reports')
        if not cached_data:
            reports = TotalRiskReport.objects.all()
            serializer = TotalRiskReportSerializer(reports, many=True)
            cache.set('total_risk_reports', serializer.data, timeout=30)  # 30 saniye cache süresi
            return Response(serializer.data)
        return Response(cached_data)

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]  # Yetkilendirme ayarları eklendi

    @method_decorator(cache_page(30))  # 30 saniye boyunca cachele
    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
        if not token:
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        # SAP HANA veritabanından veri çek
        data = fetch_hana_db_data(token)
        if data:
            try:
                with transaction.atomic():
                    TotalRiskReport.objects.all().delete()  # Mevcut tüm kayıtları sil
                    for item in data:
                        TotalRiskReport.objects.create(
                            muhatap_kod=item['MuhatapKod'],
                            satici=item.get('Satici'),
                            grup=item.get('Grup'),
                            avans_kod=item['AvansKod'],
                            muhatap_ad=item['MuhatapAd'],
                            bakiye=item['Bakiye'],
                            acik_teslimat=item['AcikTeslimat'],
                            acik_siparis=item['AcikSiparis'],
                            avans_bakiye=item.get('AvansBakiye', 0),
                            toplam_risk=item['ToplamRisk'],
                        )
                cache.delete('total_risk_reports')  # Cache'i sil
                return Response({"message": "HANA DB verileri başarıyla güncellendi ve cache temizlendi."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "HANA DB verileri çekilemedi."}, status=status.HTTP_400_BAD_REQUEST)

class LastUpdatedView(APIView):
    permission_classes = [IsAuthenticated, HasTOTALRiskAccess]  # Yetkilendirme ayarları eklendi

    def get(self, request, *args, **kwargs):
        last_updated_order = TotalRiskReport.objects.order_by('-updated_at').first()
        if last_updated_order:
            last_updated_time = timezone.localtime(last_updated_order.updated_at, timezone=timezone.get_fixed_timezone(180))
            formatted_time = last_updated_time.strftime('%d.%m.%Y %H:%M')
            return Response({"last_updated": formatted_time})
        else:
            return Response({"last_updated": "No data available"})
