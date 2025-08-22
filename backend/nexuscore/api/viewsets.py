# path: /var/www/sapb1reportsv2/backend/nexuscore/api/viewsets.py

from django.db.models import Q
from rest_framework import viewsets, status
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
    """
    Dinamik Veri Tabanı Bağlantılarını yönetir.
    Bu ViewSet, kritik bir altyapı bileşeni olduğu için SADECE
    sistem yöneticileri (admin) tarafından erişilebilirdir.
    """
    queryset = DynamicDBConnection.objects.all().order_by('title')
    serializer_class = DynamicDBConnectionSerializer
    permission_classes = [IsAdminUser]


# --- 2. Kullanıcı Alanı: Sanal Tablolar ---

class VirtualTableViewSet(viewsets.ModelViewSet):
    """
    Kullanıcıların kendi sanal tablolarını (sorgularını) yönetmesini sağlar.
    Tüm alt katmanları (services, serializers, permissions) bir orkestra şefi gibi yönetir.
    """
    serializer_class = VirtualTableSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        """
        GÜVENLİK GÖREVİ: Kullanıcıların sadece görmeye yetkili oldukları
        sanal tabloları listeler. Veri sızıntısını engeller.
        """
        user = self.request.user
        if user.is_staff:
            return VirtualTable.objects.select_related('owner', 'connection')

        return VirtualTable.objects.select_related('owner', 'connection').filter(
            Q(owner=user) |
            Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def create(self, request, *args, **kwargs):
        """
        YARATIM SÜRECİ: Yeni bir sanal tablo oluşturma operasyonunu yönetir.
        """
        # 1. Adım: Gümrük memuru (Serializer) gelen veriyi kontrol eder.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Adım: Orkestra Şefi (ViewSet), doğrulanmış veriyi alır.
        connection = serializer.validated_data['connection']
        sql_query = serializer.validated_data['sql_query']

        # 3. Adım: Şef Aşçı (Service), meta veriyi hazırlamak için göreve çağrılır.
        result = connection_manager.generate_metadata_for_query(connection, sql_query)

        if not result.get('success'):
            return Response(
                {"sql_query": [f"Sorgu çalıştırılamadı: {result.get('error')}" ]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 4. Adım: Her şey yolundaysa, Gümrük memuru son verilerle kaydı tamamlar.
        metadata = result.get('metadata')
        serializer.save(owner=request.user, column_metadata=metadata)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Not: perform_create'i sadece owner eklemek için kullanıyorduk. 
    # create metodunu tamamen override ettiğimiz için artık bu metoda ihtiyacımız kalmadı,
    # çünkü serializer.save() içine owner'ı zaten ekliyoruz. Daha temiz olması için silebiliriz.
    # def perform_create(self, serializer):
    #     serializer.save(owner=request.user)

    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        """
        PERFORMANS ZAMANI: Belirli bir sanal tablonun sorgusunu çalıştırır.
        "Çalıştır" butonunun arkasındaki güç budur.
        """
        # Kapıdaki güvenlik (Permission), bu nesneye erişim izni olup olmadığını kontrol eder.
        virtual_table = self.get_object()
        
        # Şef Aşçı (Service), yemeği (veriyi) hazırlamak için çağrılır.
        result = connection_manager.execute_virtual_table_query(virtual_table)
        
        if not result.get('success'):
            return Response({"error": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)
        
        # Yemek (veri) servis edilir.
        return Response(result)