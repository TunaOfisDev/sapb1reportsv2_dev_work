# backend/stockcardintegration/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import StockCardSerializer
from ..models.models import StockCard
from .permissions import IsStockCardAuthorizedUser
from stockcardintegration.services import send_stock_card_to_hanadb, update_stock_card_on_hanadb
from mailservice.services.stockcardintegration.update_stock_card_on_hanadb import send_stockcard_update_success_email
from mailservice.services.stockcardintegration.update_stock_card_on_hanadb import send_stockcard_update_failure_email
from stockcardintegration.services.mail.send_stockcard_summary_email import send_stockcard_summary_email
from stockcardintegration.services.sap.create_or_update_card import create_or_update_stock_card_by_code  # ✅ yeni servis import

class StockCardListView(APIView):
    """
    Stok Kartlarını listeleyen ve yeni kayıt ekleyen API.
    - `GET` → Tüm stok kartlarını listeler.
    - `POST` → Yeni bir stok kartı ekler.
    """
    permission_classes = [IsAuthenticated, IsStockCardAuthorizedUser]

    def get(self, request):
        stock_cards = StockCard.objects.all()
        serializer = StockCardSerializer(stock_cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        item_code = request.data.get("item_code")
        if not item_code:
            return Response({"error": "`item_code` alanı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

        existing_card = StockCard.objects.filter(item_code=item_code).first()
        if existing_card:
            return Response({
                "message": f"{item_code} kodlu stok kartı zaten mevcut.",
                "stock_card": StockCardSerializer(existing_card).data
            }, status=status.HTTP_409_CONFLICT)

        serializer = StockCardSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(created_by=request.user)
            send_stock_card_to_hanadb.delay(instance.id, skip_email=True)

            # ✅ Özet mail gönder (tekli)
            send_stockcard_summary_email(
                to_email=request.user.email,
                created_cards=[instance],
                error_logs=[]
            )

            return Response({
                "message": f"{item_code} kodlu stok kartı başarıyla oluşturuldu ve SAP'ya gönderildi.",
                "stock_card": StockCardSerializer(instance).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class StockCardDetailView(APIView):
    """
    Belirtilen stok kartını görüntüleme ve güncelleme API'si.
    - `GET` → Tek bir stok kartını getirir.
    - `PATCH` → Stok kartını günceller.
    - `DELETE` → Yasaklanmıştır.
    """
    permission_classes = [IsAuthenticated, IsStockCardAuthorizedUser]

    def get(self, request, pk):
        try:
            stock_card = StockCard.objects.get(pk=pk)
            serializer = StockCardSerializer(stock_card)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StockCard.DoesNotExist:
            return Response({"error": "Veri bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        try:
            stock_card = StockCard.objects.get(pk=pk)
        except StockCard.DoesNotExist:
            return Response({"error": "Veri bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

        if stock_card.hana_status == "completed":
            return Response({"error": "Bu stok kartı SAP'ya zaten başarıyla gönderilmiş. Güncellenemez."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = StockCardSerializer(stock_card, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save(updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request, pk):
        try:
            stock_card = StockCard.objects.get(pk=pk)
        except StockCard.DoesNotExist:
            return Response({"error": "Stok kartı bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

        if stock_card.hana_status == "completed":
            return Response({"error": "Bu stok kartı SAP'ya zaten gönderilmiş. Güncelleme yerine yeni kart oluşturmalısınız."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = StockCardSerializer(stock_card, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_instance = serializer.save(updated_by=request.user)

        try:
            response = update_stock_card_on_hanadb(updated_instance.id)
            send_stockcard_update_success_email(updated_instance, request.user)
            return Response({
                "message": "SAP güncelleme işlemi başarılı.",
                "hana_response": response
            }, status=status.HTTP_200_OK)

        except Exception as e:
            send_stockcard_update_failure_email(updated_instance, request.user, str(e))
            return Response({
                "error": "SAP güncelleme işlemi başarısız.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def delete(self, request, pk):
        """
        Stok kartlarını silmek kesinlikle yasaktır!
        """
        return Response({"error": "Bu veri silinemez! HANA DB üzerinde DELETE işlemi yasaktır."},
                        status=status.HTTP_403_FORBIDDEN)



class StockCardSyncTriggerView(APIView):
    """
    Stock Card senkronizasyonunu manuel olarak tetikleyen API.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            stock_card = StockCard.objects.get(pk=pk)
        except StockCard.DoesNotExist:
            return Response({"error": "Stock Card bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

        if stock_card.hana_status == "completed":
            return Response({
                "error": "Bu stok kartı zaten SAP'ya başarıyla gönderilmiş. Tekrar senkronize edilemez.",
                "hana_status": stock_card.hana_status
            }, status=status.HTTP_409_CONFLICT)

        try:
            response = send_stock_card_to_hanadb(stock_card.id)
            return Response({"message": "Senkronizasyon tamamlandı!", "response": response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Senkronizasyon sırasında hata oluştu.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class StockCardUpdateToHANAView(APIView):
    """
    SAP sistemindeki mevcut kalemleri frontend'ten güncellemek için kullanılır.
    Kullanıcı itemCode girer, detayları getirir, günceller ve SAP'ya gönderilir.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            stock_card = StockCard.objects.get(pk=pk)
        except StockCard.DoesNotExist:
            return Response({"error": "Stok kartı bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StockCardSerializer(stock_card, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_instance = serializer.save()

        try:
            response = update_stock_card_on_hanadb(updated_instance.id)

            # ✅ Yeni mail fonksiyonu ile update sonucu bildirimi
            send_stockcard_summary_email(
                to_email=request.user.email,
                created_cards=[updated_instance] if response else [],
                error_logs=[] if response else [{
                    "item_code": updated_instance.item_code,
                    "error": "SAP güncellemesi sırasında hata oluştu."
                }],
                is_update=True
            )

            return Response({
                "message": "SAP güncelleme işlemi başarılı.",
                "hana_response": response
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # ❌ Yeni mail fonksiyonu hata bildirimi
            send_stockcard_summary_email(
                to_email=request.user.email,
                created_cards=[],
                error_logs=[{
                    "item_code": updated_instance.item_code,
                    "error": str(e)
                }],
                is_update=True
            )
            return Response({
                "error": "SAP güncelleme işlemi başarısız.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkStockCardCreateView(APIView):
    """
    Çoklu Stok Kartı Oluşturma ve SAP'ya gönderme API'si.
    - `POST` → Birden fazla stok kartı oluşturur.
    """
    permission_classes = [IsAuthenticated, IsStockCardAuthorizedUser]

    def post(self, request):
        payload_list = request.data
        if not isinstance(payload_list, list):
            return Response({"error": "Gönderilen veri bir liste olmalıdır."}, status=status.HTTP_400_BAD_REQUEST)

        created_cards = []
        errors = []

        for entry in payload_list:
            item_code = entry.get("item_code")
            if not item_code:
                errors.append({"item_code": None, "error": "`item_code` alanı eksik."})
                continue

            existing_card = StockCard.objects.filter(item_code=item_code).first()
            if existing_card:
                errors.append({"item_code": item_code, "error": "Bu stok kartı zaten mevcut."})
                continue

            serializer = StockCardSerializer(data=entry)
            if serializer.is_valid():
                instance = serializer.save(created_by=request.user)
                created_cards.append(instance)
                send_stock_card_to_hanadb.delay(instance.id, skip_email=True)
            else:
                errors.append({"item_code": item_code, "error": serializer.errors})

        # ✅ Tek özet mail gönder
        send_stockcard_summary_email(
            to_email=request.user.email,
            created_cards=created_cards,
            error_logs=errors
        )

        return Response({
            "message": f"{len(created_cards)} adet stok kartı oluşturuldu ve SAP'ya gönderilmek üzere kuyruğa alındı.",
            "created_count": len(created_cards),
            "error_count": len(errors),
            "errors": errors
        }, status=status.HTTP_207_MULTI_STATUS)



class StockCardUpdateByCodeView(APIView):
    permission_classes = [IsAuthenticated, IsStockCardAuthorizedUser]

    def get(self, request, item_code):
        try:
            stock_card = StockCard.objects.get(item_code=item_code)
            serializer = StockCardSerializer(stock_card)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StockCard.DoesNotExist:
            return Response({"error": "Stok kartı bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, item_code):
        try:
            updated_instance = create_or_update_stock_card_by_code(item_code, request.data, request.user)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = update_stock_card_on_hanadb(updated_instance.id)

            send_stockcard_summary_email(
                to_email=request.user.email,
                updated_cards=[updated_instance],
                error_logs=[]
            )

            return Response({
                "message": "SAP güncelleme işlemi başarılı.",
                "hana_response": response
            }, status=status.HTTP_200_OK)

        except Exception as e:
            send_stockcard_summary_email(
                to_email=request.user.email,
                updated_cards=[],
                error_logs=[{
                    "item_code": updated_instance.item_code,
                    "error": str(e)
                }]
            )
            return Response({
                "error": "SAP güncelleme işlemi başarısız.",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
