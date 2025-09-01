# path: /var/www/sapb1reportsv2/backend/nexuscore/api/viewsets.py

from django.db.models import Q
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# Tüm katmanlarımızdan gerekli bileşenleri import ediyoruz
from ..models import DynamicDBConnection, VirtualTable, SharingStatus, ReportTemplate
from .serializers import DynamicDBConnectionSerializer, VirtualTableSerializer, ReportTemplateSerializer
from .permissions import IsOwnerOrPublic
# ### YENİ: pivot_manager'ı da servislerimize dahil ediyoruz ###
from ..services import connection_manager, template_manager, pivot_manager

# --- 1. Altyapı Yönetimi: Veri Tabanı Bağlantıları ---

class DynamicDBConnectionViewSet(viewsets.ModelViewSet):
    # ... (Bu ViewSet'te bir değişiklik yok, aynı kalıyor) ...
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

# --- 2. Kullanıcı Alanı: Sanal Tablolar ---

class VirtualTableViewSet(viewsets.ModelViewSet):
    # ... (Bu ViewSet'te bir değişiklik yok, aynı kalıyor) ...
    serializer_class = VirtualTableSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return VirtualTable.objects.select_related('owner', 'connection').all()
        return VirtualTable.objects.select_related('owner', 'connection').filter(
            Q(owner=user) |
            Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
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

# --- 3. Kullanıcı Alanı: Rapor Şablonları ---

class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        # ... (bu metod aynı kalıyor) ...
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ReportTemplate.objects.select_related('owner', 'source_virtual_table').all()
        return ReportTemplate.objects.select_related('owner', 'source_virtual_table').filter(
            Q(owner=user) |
            Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def perform_create(self, serializer):
        # ... (bu metod aynı kalıyor) ...
        serializer.save(owner=self.request.user)

    # ### GÜNCELLEME: execute aksiyonu artık "akıllı santral" gibi çalışıyor ###
    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        """
        Bir rapor şablonunu çalıştırır. Raporun türüne göre ('pivot' veya 'detail')
        doğru servis katmanını çağırır.
        """
        report_template = self.get_object()
        config = report_template.configuration_json

        # Rapor türünü kontrol et, eğer pivot ise pivot_manager'ı çağır.
        if config.get('report_type') == 'pivot':
            result = pivot_manager.generate_pivot_data(report_template)
        else:
            # Değilse, standart detay raporu için template_manager'ı çağır.
            result = template_manager.execute_report_template(report_template)
        
        if not result.get('success'):
            return Response({"error": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)