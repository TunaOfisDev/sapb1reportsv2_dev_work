# backend/hanadbintegration/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSAPAuthorizedUser
from .serializers import HANADBIntegrationSerializer
from .services import HANADBServiceLayer
from ..models.models import HANADBIntegration
from ..utils.logs import log_hana_error

class HANADBIntegrationListView(APIView):
    """
    HANA DB Entegrasyon kayıtlarını listeleyen ve yeni kayıt ekleyen API.
    """
    permission_classes = [IsAuthenticated, IsSAPAuthorizedUser]

    def get(self, request):
        """
        HANA DB Entegrasyon nesnelerini listeleme.
        """
        hanadb_integrations = HANADBIntegration.objects.all()
        serializer = HANADBIntegrationSerializer(hanadb_integrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Yeni bir HANA DB Entegrasyon nesnesi oluşturma ve HANA DB'ye gönderme.
        """
        serializer = HANADBIntegrationSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            
            # HANA DB Service Layer ile iletişim
            hana_service = HANADBServiceLayer()
            try:
                response = hana_service.post_data("Items", instance.integration_type)
                instance.mark_as_synced()  # Başarılıysa senkronize olarak işaretle
                return Response(response, status=status.HTTP_201_CREATED)
            except Exception as e:
                log_hana_error(str(e))
                instance.mark_as_failed()  # Başarısız olarak işaretle
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HANADBIntegrationDetailView(APIView):
    """
    HANA DB Entegrasyon nesnesini görüntüleme ve güncelleme API'si.
    """
    permission_classes = [IsAuthenticated, IsSAPAuthorizedUser]

    def get(self, request, pk):
        """
        Belirtilen HANA DB Entegrasyon nesnesini getirir.
        """
        try:
            hanadb_integration = HANADBIntegration.objects.get(pk=pk)
            serializer = HANADBIntegrationSerializer(hanadb_integration)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except HANADBIntegration.DoesNotExist:
            return Response({"error": "Veri bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        """
        HANA DB Entegrasyon nesnesini günceller ve HANA DB'ye değişiklikleri gönderir.
        """
        try:
            hanadb_integration = HANADBIntegration.objects.get(pk=pk)
        except HANADBIntegration.DoesNotExist:
            return Response({"error": "Veri bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HANADBIntegrationSerializer(hanadb_integration, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            
            # HANA DB Service Layer ile iletişim
            hana_service = HANADBServiceLayer()
            try:
                response = hana_service.patch_data(f"Items('{instance.integration_type}')", instance.integration_type)
                instance.mark_as_synced()  # Başarılı güncelleme
                return Response(response, status=status.HTTP_200_OK)
            except Exception as e:
                log_hana_error(str(e))
                instance.mark_as_failed()  # Başarısız güncelleme
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
