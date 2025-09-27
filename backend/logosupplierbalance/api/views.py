# backend/logosupplierbalance/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import LogoSupplierBalanceSerializer
from ..models.models import SupplierBalance
from ..utils.data_fetcher import fetch_logo_db_data
from django.core.cache import cache
from loguru import logger

class SupplierBalanceListView(APIView):
    """
    Django lokal veritabanındaki tüm SupplierBalance kayıtlarını listeler.
    """
    def get(self, request, *args, **kwargs):
        cached_data = cache.get('supplier_balance')
        if not cached_data:
            balances = SupplierBalance.objects.all()
            serializer = LogoSupplierBalanceSerializer(balances, many=True)
            cache.set('supplier_balance', serializer.data, timeout=30)  # 30 saniye cache süresi
            return Response(serializer.data)
        return Response(cached_data)


class FetchLogoDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
        if not token:
            return Response({"error": "Token sağlanmadı."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = fetch_logo_db_data(token)
            if not data:  # Veri yoksa uygun bir cevap dön
                return Response({"error": "Veri alınamadı veya boş."}, status=status.HTTP_204_NO_CONTENT)

            with transaction.atomic():
                # Mevcut tüm kayıtları sil
                SupplierBalance.objects.all().delete()
                # Yeni verileri oluştur
                for item in data:
                    SupplierBalance.objects.create(
                        cari_kodu=item['Cari Kodu'],
                        cari_aciklamasi=item['Cari Açıklaması'],
                        bakiye_borc=item['BakiyeBorc'],
                        bakiye_alacak=item['BakiyeAlacak'],
                    )
            cache.delete('supplier_balance')
            return Response({"message": "LOGO DB verileri başarıyla güncellendi ve cache temizlendi."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"LOGO verileri çekerken hata oluştu: {e}")
            return Response({
                "error": "Veri güncelleme işlemi sırasında bir hata oluştu.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
