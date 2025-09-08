# path: backend/nexuscore/api/viewsets.py
import logging
from django.db.models import Q
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# --- YENİ İMPORTLAR ---
# Artık "dahi" servislerimize ihtiyacımız var: connection_manager VE pivot_manager.
from ..services import connection_manager, pivot_manager
# Yeni modellerimizin ve serializer'larımızın tamamını import et
from ..models import (
    DynamicDBConnection, VirtualTable, SharingStatus, 
    ReportTemplate, DataApp, AppRelationship
)
from .serializers import (
    DynamicDBConnectionSerializer, VirtualTableSerializer, ReportTemplateSerializer,
    DataAppSerializer, AppRelationshipSerializer
)
from .permissions import IsOwnerOrPublic

logger = logging.getLogger(__name__)

# --- 1. Altyapı Yönetimi: Veri Tabanı Bağlantıları ---
class DynamicDBConnectionViewSet(viewsets.ModelViewSet):
    """ (Bu sınıf değişmedi) """
    queryset = DynamicDBConnection.objects.all().order_by('title')
    serializer_class = DynamicDBConnectionSerializer
    permission_classes = [IsAdminUser]

    # ... (create, retrieve, test_connection metodları aynı kalıyor) ...
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
    """ (Bu sınıf değişmedi) """
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
        # Bu 'execute', Playground'un tek bir tablodan ham veri alması için hala gerekli.
        virtual_table = self.get_object()
        result = connection_manager.execute_virtual_table_query(virtual_table)
        if not result.get('success'):
            return Response({"error": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


# --- 3. YENİ: Veri Uygulamaları (DataApp) ViewSet ---
class DataAppViewSet(viewsets.ModelViewSet):
    """
    Yeni Veri Uygulamalarını (ilişkisel modeller) yönetmek için API endpoint'i.
    """
    serializer_class = DataAppSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        """ Sadece sahip olunan veya herkese açık olan DataApp'leri listele. """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return DataApp.objects.select_related('owner', 'connection').prefetch_related('relationships').all()
        return DataApp.objects.select_related('owner', 'connection').prefetch_related('relationships').filter(
            Q(owner=user) |
            Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def perform_create(self, serializer):
        # Serializer zaten context'ten user'ı alıp atıyor, ama burada tekrar garanti edebiliriz.
        serializer.save(owner=self.request.user)


# --- 4. YENİ: Uygulama İlişkileri (AppRelationship) ViewSet ---
class AppRelationshipViewSet(viewsets.ModelViewSet):
    """
    Bir DataApp içindeki JOIN ilişkilerini yönetmek için API endpoint'i.
    Güvenlik, serializer katmanında doğrulanır (tabloların app'e ait olması vb.)
    """
    serializer_class = AppRelationshipSerializer
    permission_classes = [IsAuthenticated] # Sadece giriş yapmış kullanıcılar ilişki yaratabilir

    def get_queryset(self):
        """ Sadece KENDİ sahip olduğu App'lerin ilişkilerini yönetebilir. """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return AppRelationship.objects.select_related('app', 'left_table', 'right_table').all()
        
        # Kullanıcının sahip olduğu veya düzenleyebileceği App'lere ait ilişkileri getir
        editable_apps = DataApp.objects.filter(
            Q(owner=user) | Q(sharing_status=SharingStatus.PUBLIC_EDITABLE)
        )
        return AppRelationship.objects.select_related('app', 'left_table', 'right_table').filter(
            app__in=editable_apps
        )


# --- 5. GÜNCELLENMİŞ: Rapor Şablonları ViewSet ---
class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        """
        DÜZELTME: Artık 'source_virtual_table' yerine 'source_data_app'
        üzerinden ilişki kuruyor ve ön-yükleme (prefetch) yapıyoruz.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ReportTemplate.objects.select_related('owner', 'source_data_app__connection').all()
        return ReportTemplate.objects.select_related('owner', 'source_data_app__connection').filter(
            Q(owner=user) |
            Q(sharing_status__in=[SharingStatus.PUBLIC_READONLY, SharingStatus.PUBLIC_EDITABLE])
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # ### STRATEJİK DEVİR: 'execute' ARTIK "DAHİ" BİR İŞLEMCİDİR ###
    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        """
        BİR RAPORU ÇALIŞTIRIR VE PIVOT EDER.
        
        Frontend'e (React) artık HAM VERİ göndermez.
        
        Bunun yerine, 'pivot_manager' servisimizi çağırır. Bu servis:
        1. Raporun DataApp'ini ve ilişkilerini okur.
        2. 'data_app_manager' ile devasa CTE + JOIN sorgusunu oluşturur.
        3. Raporun pivot konfigürasyonunu (GROUP BY) bu sorguya uygular.
        4. Veritabanında çalıştırır ve SADECE NİHAİ, ÖZETLENMİŞ PIVOT SONUCUNU döndürür.
        
        Bu, backend'in "dahi" moda geri dönüşüdür ve çoklu veri için TEK ölçeklenebilir yoldur.
        """
        try:
            report_template = self.get_object()
            
            # 1. Raporun bir veri modeline bağlı olduğundan emin ol
            # (Migration sonrası bazı eski raporlar 'NULL' olabilir)
            if not report_template.source_data_app:
                raise serializers.ValidationError(
                    "Bu rapor geçerli bir Veri Uygulamasına (DataApp) bağlı değil. Lütfen rapor ayarlarını güncelleyin."
                )

            # 2. "Dahi" pivot servisimizi çağır
            # Bu fonksiyon zaten içinde {success, columns, rows} veya {success, error} döndürür.
            result = pivot_manager.generate_pivot_data(report_template)
            
            # 3. Servisten bir hata geldiyse, bunu 400 Bad Request olarak döndür
            if not result.get('success'):
                return Response({"error": result.get('error')}, status=status.HTTP_400_BAD_REQUEST)

            # 4. Başarılı: Frontend'e pişmiş, hazır pivot verisini yolla
            return Response(result)
            
        except serializers.ValidationError as e:
            # Yakalanan spesifik validasyon hataları (örn: App bağlı değil)
             return Response({"error": e.detail[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Diğer tüm beklenmedik sunucu hataları
            logger.error(f"ReportTemplate execute (ID: {pk}) hatası: {e}", exc_info=True)
            return Response({"error": f"Rapor çalıştırılırken sunucuda beklenmedik bir hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)