# backend/logo_supplier_receivables_aging/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..tasks import save_raw_transactions, generate_closing_invoices
from ..serializers import SupplierAgingSummarySerializer
from ..models.closinginvoice import SupplierAgingSummary
from ..models.models import SupplierRawTransaction

from django.db.models import Max


class FetchHanaDataView(APIView):
    """
    HANA'dan veri çeker ve yaşlandırma analizi oluşturur.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return Response({'error': 'Token eksik.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Tüm eski verileri sil (yeniden hesaplama garantisi için)
        SupplierRawTransaction.objects.all().delete()
        SupplierAgingSummary.objects.all().delete()

        save_raw_transactions(token)
        generate_closing_invoices()

        return Response({'message': 'Ham veri alındı ve analiz tablosu güncellendi.'}, status=status.HTTP_200_OK)



class SupplierAgingSummaryView(APIView):
    """
    Tüm tedarikçilerin yaşlandırılmış özet alacak verilerini döner.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = SupplierAgingSummary.objects.all().order_by('cari_kod')
        serializer = SupplierAgingSummarySerializer(data, many=True)
        return Response(serializer.data)


class LastUpdatedView(APIView):
    """
    Ham verideki en son güncelleme tarihini döner.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = SupplierRawTransaction.objects.aggregate(last_updated=Max('updated_at'))
        return Response({"last_updated": latest['last_updated']})
