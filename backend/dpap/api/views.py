# backend/dpap/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models.models import API, APIAccessPermission, APIAuditLog
from ..serializers import APISerializer, APIAccessPermissionSerializer, APIAuditLogSerializer
from ..utils.utils import has_crud_permission, log_api_access


class APIAccessListView(APIView):
    """
    API erişim izinlerini listeleyen view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Kullanıcıya ait API erişimlerini listeler.
        """
        user = request.user
        api_accesses = API.objects.filter(is_active=True)
        serializer = APISerializer(api_accesses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIAccessDetailView(APIView):
    """
    Belirli bir API'nin erişim izinlerinin detaylarını gösterir.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, api_id, *args, **kwargs):
        """
        API erişim izni detaylarını döner.
        """
        api_access = get_object_or_404(API, pk=api_id)
        serializer = APISerializer(api_access)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIAccessPermissionListView(APIView):
    """
    API erişim izinlerine ait CRUD yetkilerini listeleyen view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Kullanıcıya ait API CRUD yetkilerini listeler.
        """
        user = request.user
        api_permissions = APIAccessPermission.objects.filter(
            departments__in=user.departments.all()
        ) | APIAccessPermission.objects.filter(
            positions__in=user.positions.all()
        )
        serializer = APIAccessPermissionSerializer(api_permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIAuditLogListView(APIView):
    """
    API erişim loglarını listeleyen view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Kullanıcıya ait API erişim loglarını listeler.
        """
        audit_logs = APIAuditLog.objects.filter(user=request.user)
        serializer = APIAuditLogSerializer(audit_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APIAccessCreateView(APIView):
    """
    API'ye erişim izni oluşturma view'i.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        API erişim izni oluşturur.
        """
        if not has_crud_permission(request.user, 'api_name', 'create'):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = APISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_api_access(request.user, 'api_name', success=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIAccessUpdateView(APIView):
    """
    API erişim izni güncelleme view'i.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, api_id, *args, **kwargs):
        """
        Belirli bir API erişim iznini günceller.
        """
        api_access = get_object_or_404(API, pk=api_id)
        if not has_crud_permission(request.user, api_access.name, 'update'):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = APISerializer(api_access, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_api_access(request.user, api_access.name, success=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIAccessDeleteView(APIView):
    """
    API erişim izni silme view'i.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, api_id, *args, **kwargs):
        """
        Belirli bir API erişim iznini siler.
        """
        api_access = get_object_or_404(API, pk=api_id)
        if not has_crud_permission(request.user, api_access.name, 'delete'):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        api_access.delete()
        log_api_access(request.user, api_access.name, success=True)
        return Response({'detail': 'API access deleted.'}, status=status.HTTP_204_NO_CONTENT)

