# path: backend/nexuscore/api/viewsets.py
import logging
from django.db.models import Q
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from ..services import connection_manager, pivot_manager
from ..models import (
    DynamicDBConnection, VirtualTable, SharingStatus, 
    ReportTemplate, DataApp, AppRelationship, DBTypeMapping # Yeni modelimizi import ediyoruz
)
from .serializers import (
    DynamicDBConnectionSerializer, VirtualTableSerializer, ReportTemplateSerializer,
    DataAppSerializer, AppRelationshipSerializer, DBTypeMappingSerializer # Yeni serializer'ı import ediyoruz
)
from .permissions import IsOwnerOrPublic

logger = logging.getLogger(__name__)

# --- YENİ: Yönetici Paneli için Veri Tipi Eşleştirme ViewSet ---
class DBTypeMappingViewSet(viewsets.ModelViewSet):
    """
    Sistem yöneticileri için veri tipi eşleştirmelerini yöneten API endpoint'i.
    Bu, arka planda otomatik olarak keşfedilen tiplerin manuel olarak düzeltilmesine olanak tanır.
    """
    queryset = DBTypeMapping.objects.all().order_by('db_type', 'source_type')
    serializer_class = DBTypeMappingSerializer
    permission_classes = [IsAdminUser] # Sadece yöneticiler bu alana erişebilir

# --- 1. Altyapı Yönetimi: Veri Tabanı Bağlantıları ---
class DynamicDBConnectionViewSet(viewsets.ModelViewSet):
    queryset = DynamicDBConnection.objects.all().order_by('title')
    serializer_class = DynamicDBConnectionSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['config_json'] = instance.config_json
        return Response(data)

    @action(detail=True, methods=['post'], url_path='test_connection')
    def test_connection(self, request, pk=None):
        connection_instance = self.get_object()
        config = connection_instance.config_json
        db_type = connection_instance.db_type
        is_successful, message = connection_manager.test_connection_config(config, db_type)
        if not is_successful:
            return Response({'status': 'failure', 'message': message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success', 'message': message})
    
    @action(detail=False, methods=['get'], url_path='supported-types', permission_classes=[IsAuthenticated])
    def supported_types(self, request):
        from ..utils.popular_db_list import POPULAR_DB_LIST
        return Response(POPULAR_DB_LIST)


# --- 2. Kullanıcı Alanı: Sanal Tablolar ---
class VirtualTableViewSet(viewsets.ModelViewSet):
    serializer_class = VirtualTableSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return VirtualTable.objects.select_related('owner', 'connection').all()
        return VirtualTable.objects.select_related('owner', 'connection').filter(
            Q(owner=user) | Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        virtual_table = self.get_object()
        result = connection_manager.execute_virtual_table_query(virtual_table)
        if not result.get('success'):
            return Response({"error": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


# --- 3. Veri Uygulamaları (DataApp) ViewSet ---
class DataAppViewSet(viewsets.ModelViewSet):
    serializer_class = DataAppSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return DataApp.objects.select_related('owner', 'connection').prefetch_related('relationships').all()
        return DataApp.objects.select_related('owner', 'connection').prefetch_related('relationships').filter(
            Q(owner=user) | Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# --- 4. Uygulama İlişkileri (AppRelationship) ViewSet ---
class AppRelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = AppRelationshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return AppRelationship.objects.select_related('app', 'left_table', 'right_table').all()
        
        editable_apps = DataApp.objects.filter(
            Q(owner=user) | Q(sharing_status=SharingStatus.PUBLIC_EDITABLE)
        )
        return AppRelationship.objects.select_related('app', 'left_table', 'right_table').filter(
            app__in=editable_apps
        )


# --- 5. Rapor Şablonları ViewSet ---
class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ReportTemplate.objects.select_related('owner', 'source_data_app__connection').all()
        return ReportTemplate.objects.select_related('owner', 'source_data_app__connection').filter(
            Q(owner=user) | Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        try:
            report_template = self.get_object()
            if not report_template.source_data_app:
                raise serializers.ValidationError("Bu rapor geçerli bir Veri Uygulamasına (DataApp) bağlı değil. Lütfen rapor ayarlarını güncelleyin.")

            result = pivot_manager.generate_pivot_data(report_template)
            
            if not result.get('success'):
                return Response({"error": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

            return Response(result)
            
        except serializers.ValidationError as e:
            return Response({"error": e.detail[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"ReportTemplate execute (ID: {pk}) hatası: {e}", exc_info=True)
            return Response({"error": f"Rapor çalıştırılırken sunucuda beklenmedik bir hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)