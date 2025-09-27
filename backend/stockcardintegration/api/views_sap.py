# path: backend/stockcardintegration/api/views_sap.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsStockCardAuthorizedUser
from stockcardintegration.services import get_item_from_sap  # yeni servis fonksiyonu

class SAPLiveStockCardFetchView(APIView):
    """
    SAP Business One HANA'dan canlı stok kartı verisi getirir.
    Sadece okuma amaçlıdır, local veritabanı ile ilgisi yoktur.
    """
    permission_classes = [IsAuthenticated, IsStockCardAuthorizedUser]

    def get(self, request, item_code):
        try:
            data = get_item_from_sap(item_code)
            return Response(data, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
