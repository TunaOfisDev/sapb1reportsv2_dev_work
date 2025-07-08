# backend/rawmaterialwarehousestock/api/views.py
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from ..models.models import RawMaterialWarehouseStock
from ..serializers import RawMaterialWarehouseStockSerializer
from ..tasks import fetch_and_update_hana_data
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from django.db import IntegrityError

logger = logging.getLogger(__name__)

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            jwt_token = str(refresh.access_token)
            cache.set('jwt_token', jwt_token, timeout=None)

            return Response({
                'refresh': str(refresh),
                'access': jwt_token,
            })

        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        token = str(request.auth)
        fetch_and_update_hana_data.delay(token)
        stocks = RawMaterialWarehouseStock.objects.all().distinct('kalem_kod')
        serializer = RawMaterialWarehouseStockSerializer(stocks, many=True)
        return Response(serializer.data)

class FetchHanaDataView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        token = str(request.auth)
        fetch_and_update_hana_data.delay(token)
        return Response({
            "message": "Veri çekme işlemi başlatıldı. Sonuçlar arka planda güncellenecek."
        }, status=status.HTTP_200_OK)

class UpdateSelectionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            is_hammadde = request.data.get('isHammadde')
            logger.info(f"Received isHammadde: {is_hammadde}")

            if is_hammadde is not None:
                RawMaterialWarehouseStock.objects.filter(kalem_grup_ad="HAMMADDE").update(secili=is_hammadde)
                logger.info(f"Updated selection for HAMMADDE to {is_hammadde}")
                return Response({'message': 'Selection updated successfully'}, status=status.HTTP_200_OK)
            else:
                logger.warning("Invalid request: isHammadde is None")
                return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in UpdateSelectionView: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateZeroStockVisibilityView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            hide_zero_stock = request.data.get('hideZeroStock')
            logger.info(f"Received hideZeroStock: {hide_zero_stock}")
            
            if hide_zero_stock is not None:
                request.session['hide_zero_stock'] = hide_zero_stock
                logger.info(f"Updated hide_zero_stock in session to {hide_zero_stock}")
                return Response({'message': 'Zero stock visibility updated successfully'}, status=status.HTTP_200_OK)
            else:
                logger.warning("Invalid request: hideZeroStock is None")
                return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in UpdateZeroStockVisibilityView: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilteredListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        token = str(request.auth)
        fetch_and_update_hana_data.delay(token)
        
        stocks = RawMaterialWarehouseStock.objects.all()
        
        if request.session.get('hide_zero_stock'):
            stocks = stocks.exclude(depo_stok=0, siparis_edilen_miktar=0)
        
        stocks = stocks.distinct('kalem_kod')
        serializer = RawMaterialWarehouseStockSerializer(stocks, many=True)
        return Response(serializer.data)

class CreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = RawMaterialWarehouseStockSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'error': 'Kalem kodu zaten mevcut.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            stock = RawMaterialWarehouseStock.objects.get(pk=pk)
        except RawMaterialWarehouseStock.DoesNotExist:
            return Response({'error': 'Kayıt bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RawMaterialWarehouseStockSerializer(stock, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except IntegrityError:
                return Response({'error': 'Kalem kodu zaten mevcut.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)