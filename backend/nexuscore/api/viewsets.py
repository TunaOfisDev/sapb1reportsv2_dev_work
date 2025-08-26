# path: /var/www/sapb1reportsv2/backend/nexuscore/api/viewsets.py

from django.db.models import Q
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response


# Tüm katmanlarımızdan gerekli bileşenleri import ediyoruz.
from ..models import DynamicDBConnection, VirtualTable, SharingStatus
from .serializers import DynamicDBConnectionSerializer, VirtualTableSerializer
from .permissions import IsOwnerOrPublic
from ..services import connection_manager

# --- 1. Altyapı Yönetimi: Veri Tabanı Bağlantıları ---

class DynamicDBConnectionViewSet(viewsets.ModelViewSet):
    queryset = DynamicDBConnection.objects.all().order_by('title')
    serializer_class = DynamicDBConnectionSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # ### DÜZELTME 2: retrieve metodu ###
    def retrieve(self, request, *args, **kwargs):
        """
        Tek bir bağlantının detayını getirir. Bu metod, "Düzenle" formunu
        doldurmak için `config_json` dahil TÜM veriyi döndürür.
        """
        instance = self.get_object()
        # Standart serializer'ı kullanarak, `to_representation`'daki maskelemeyi atlayıp
        # ham veriyi döndürüyoruz.
        serializer = self.get_serializer(instance)
        data = serializer.data
        # `to_representation` maskelemesini atlamak için, ham veriyi modelden alalım
        data['config_json'] = instance.config_json
        return Response(data)

    @action(detail=True, methods=['post'], url_path='test_connection')
    def test_connection(self, request, pk=None):
        """
        Belirtilen ID'ye sahip veritabanı bağlantısını test eder.
        """
        connection_instance = self.get_object()
        config = connection_instance.config_json
        # ### DÜZELTME 1: Eksik olan `db_type` parametresini ekliyoruz ###
        db_type = connection_instance.db_type
        
        is_successful, message = connection_manager.test_connection_config(config, db_type)
        
        if not is_successful:
            return Response(
                {'status': 'failure', 'message': message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'status': 'success', 'message': message})

# --- 2. Kullanıcı Alanı: Sanal Tablolar ---

class VirtualTableViewSet(viewsets.ModelViewSet):
    """
    Kullanıcıların kendi sanal tablolarını (sorgularını) yönetmesini sağlar.
    """
    serializer_class = VirtualTableSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        """
        Kullanıcıların sadece kendi sahip oldukları veya herkese açık olan
        sanal tabloları görmesini sağlar.
        """
        user = self.request.user
        # Adminler tüm kayıtları görebilir.
        if user.is_staff or user.is_superuser:
            return VirtualTable.objects.select_related('owner', 'connection').all()

        return VirtualTable.objects.select_related('owner', 'connection').filter(
            Q(owner=user) |
            Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def perform_create(self, serializer):
        """
        Yeni bir sanal tablo oluşturulurken, sahibi otomatik olarak o anki kullanıcı olarak ayarlar
        ve servis katmanı aracılığıyla meta veriyi oluşturur.
        """
        connection = serializer.validated_data['connection']
        sql_query = serializer.validated_data['sql_query']

        # Servis katmanını çağırarak sorgudan meta veriyi (kolon isimleri) al.
        result = connection_manager.generate_metadata_for_query(connection, sql_query)

        if not result.get('success'):
            # Eğer sorgu hatalıysa ve meta veri üretilemiyorsa, validation error fırlat.
            raise serializers.ValidationError({
                "sql_query": f"Sorgu çalıştırılamadı: {result.get('error')}"
            })
        
        metadata = result.get('metadata')
        serializer.save(owner=self.request.user, column_metadata=metadata)

    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        """
        Belirli bir sanal tablonun sorgusunu çalıştırır ve sonucu döndürür.
        """
        virtual_table = self.get_object()
        
        # İş mantığını servis katmanından çağırıyoruz.
        result = connection_manager.execute_virtual_table_query(virtual_table)
        
        if not result.get('success'):
            return Response({"error": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)