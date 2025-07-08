# File: backend/procure_compare/api/views.py

from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from procure_compare.models import (
    PurchaseOrder,
    PurchaseQuote,
    PurchaseComparison,
    PurchaseApproval
)

from procure_compare.api.serializers import (
    PurchaseOrderSerializer,
    PurchaseQuoteSerializer,
    PurchaseComparisonSerializer,
    PurchaseApprovalSerializer
)

from procure_compare.services import (
    fetch_hana_procure_compare_data,
    fetch_item_purchase_history,
    sync_procure_compare_data,
    create_approval_record
)
from .serializers import ApprovalHistoryGroupedSerializer
from mailservice.services.send_procure_compare_approval_email import ProcureCompareApprovalMailService
from sapreports.celery import get_or_create_token


class PurchaseOrderListView(generics.ListAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class PurchaseQuoteListView(generics.ListAPIView):
    queryset = PurchaseQuote.objects.all()
    serializer_class = PurchaseQuoteSerializer


class PurchaseComparisonListView(generics.ListAPIView):
    queryset = PurchaseComparison.objects.all()
    serializer_class = PurchaseComparisonSerializer


class SyncProcureCompareFromHANAView(APIView):
    """
    Kullanıcının manuel olarak HANA'dan veri çekmesini ve PostgreSQL'e kaydetmesini sağlar.
    """

    def post(self, request, *args, **kwargs):
        token = get_or_create_token()
        if not token:
            return Response({"error": "Token alınamadı"}, status=status.HTTP_401_UNAUTHORIZED)

        hana_data = fetch_hana_procure_compare_data(token)
        if not hana_data:
            return Response({"error": "HANA'dan veri alınamadı"}, status=status.HTTP_502_BAD_GATEWAY)

        sync_procure_compare_data(hana_data)
        return Response({"status": "Veri başarıyla senkronize edildi"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approval_action(request):
    """
    Satınalma onay, kısmi onay, red veya onay iptal işlemi yapar.
    'Satin_Alma_Onay' departmanına üye kullanıcıların ilk onayı yeterlidir.
    Her işlem sonrası ilgili kişilere e-posta gönderimi yapılır.
    """
    try:
        data = request.data.copy()
        data['kullanici'] = request.user.email  # Authenticated user email

        approval = create_approval_record(data)

        try:
            mail_sent = ProcureCompareApprovalMailService().send_mail(approval)
            if not mail_sent:
                print(f"[MAIL ERROR] Mail gönderimi başarısız oldu. Action: {approval.action}")
        except Exception as e:
            print(f"[MAIL EXCEPTION] {str(e)}")

        return Response({
            "success": True,
            "message": f"Onay işlemi başarılı: {approval.action.upper()}",
            "data": {
                "belge_no": approval.belge_no,
                "uniq_detail_no": approval.uniq_detail_no,
                "action": approval.action,
                "aciklama": approval.aciklama,
                "kullanici": approval.kullanici.email,
                "created_at": approval.created_at,
            }
        }, status=status.HTTP_201_CREATED)

    except ValidationError as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApprovalHistoryView(generics.ListAPIView):
    serializer_class = PurchaseApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        belge_no = self.request.query_params.get('belge_no')
        uniq_detail_no = self.request.query_params.get('uniq_detail_no')
        queryset = PurchaseApproval.objects.all()

        if belge_no:
            queryset = queryset.filter(belge_no=belge_no)
        if uniq_detail_no:
            queryset = queryset.filter(uniq_detail_no=uniq_detail_no)

        return queryset.order_by('-created_at')


class ApprovalHistoryGroupedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        belge_no = request.query_params.get('belge_no')
        uniq_detail_no = request.query_params.get('uniq_detail_no')

        if not belge_no or not uniq_detail_no:
            return Response({"error": "Belge numarası ve uniq_detail_no zorunludur"}, status=400)

        records = PurchaseApproval.objects.filter(
            belge_no=belge_no,
            uniq_detail_no=uniq_detail_no
        ).order_by('created_at')

        history = []
        for idx, rec in enumerate(records, 1):
            history.append({
                "sira": idx,
                "action": rec.get_action_display(),
                "kullanici": rec.kullanici.email if rec.kullanici else "Bilinmeyen",
                "tarih": rec.created_at.strftime("%d.%m.%Y %H:%M"),
                "aciklama": rec.aciklama
            })

        return Response({
            "belge_no": belge_no,
            "uniq_detail_no": uniq_detail_no,
            "gecmis": ApprovalHistoryGroupedSerializer(history, many=True).data
        })


class ItemPurchaseHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        item_code = request.query_params.get('item_code')

        if not item_code:
            return Response({'error': 'item_code parametresi gerekli.'}, status=400)

        result = fetch_item_purchase_history(token, item_code)

        if result is not None:
            return Response({
                "source": result["source"],
                "records": result["data"]
            })
        else:
            return Response({'error': 'Veri çekilemedi.'}, status=500)


