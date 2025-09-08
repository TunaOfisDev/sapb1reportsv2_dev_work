# path: backend/nexuscore/api/viewsets.py

from django.db.models import Q
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# template_manager ve pivot_manager'a execute() içinde ihtiyacımız YOK.
# Sadece ham veri kaynağı olan connection_manager'a ihtiyacımız var.
from ..models import DynamicDBConnection, VirtualTable, SharingStatus, ReportTemplate
from .serializers import DynamicDBConnectionSerializer, VirtualTableSerializer, ReportTemplateSerializer
from .permissions import IsOwnerOrPublic
from ..services import connection_manager # Sadece bu servis gerekiyor.

# --- 1. Altyapı Yönetimi: Veri Tabanı Bağlantıları ---
class DynamicDBConnectionViewSet(viewsets.ModelViewSet):
    # ... (Bu kod bloğu değişmedi, olduğu gibi kalıyor) ...
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
    # ... (Bu kod bloğu değişmedi, olduğu gibi kalıyor) ...
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
        # Bu 'execute' (sanal tabloyu çalıştırma) backend'den ham veri almak için kullanılır.
        # Playground'un kullandığı budur ve bu DOĞRUDUR.
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

    # ### MİMARİ DÜZELTME: 'execute' ARTIK "APTAL" BİR VERİ AKTARICIDIR ###
    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        """
        Bir raporu çalıştırır. 
        Frontend'in (React) ihtiyacı olan iki şeyi döndürür:
        1. Raporun Konfigürasyonu (Frontend'in 'nasıl' render edeceğini bilmesi için)
        2. Ham Veri (Frontend'in 'neyi' render edeceğini bilmesi için)
        
        Bu endpoint, backend'de pivot VEYA filtreleme yapmaz. 
        Tüm bu mantık frontend'de (PivotRenderer ve DetailBuilder) ele alınır.
        """
        try:
            report_template = self.get_object()
            
            # 1. Ham veriyi al (Tıpkı VirtualTable.execute gibi)
            source_table = report_template.source_virtual_table
            if not source_table:
                raise serializers.ValidationError("Raporun bağlı olduğu bir sanal tablo kaynağı yok.")

            raw_data_result = connection_manager.execute_virtual_table_query(source_table)
            
            if not raw_data_result.get('success'):
                # Ham veri sorgusu başarısız olursa, hatayı döndür
                return Response({"error": raw_data_result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Konfigürasyonu al
            config = report_template.configuration_json
            
            # 3. Frontend'e istediği paketi (payload) yolla
            payload = {
                "configuration": config,
                "data": raw_data_result 
                # (raw_data_result zaten {success, columns, rows} formatındadır)
            }
            
            return Response(payload)
            
        except Exception as e:
            # Genel bir hata olursa yakala
            return Response({"error": f"Rapor çalıştırılırken sunucu hatası: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)