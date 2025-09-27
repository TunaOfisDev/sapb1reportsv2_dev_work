# backend/productconfig_simulator/api/simulation_job_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

import csv
import json
import logging
from datetime import datetime

from ..models.simulation_job import SimulationJob
from ..models.simulated_variant import SimulatedVariant
from ..models.simulation_error import SimulationError

from ..serializers import (
    SimulationJobCreateSerializer,
    SimulationJobDetailSerializer,
    SimulationJobListSerializer,
    SimulationStatusSerializer,
    SimulatedVariantListSerializer,
    SimulatedVariantExportSerializer,
    SimulationErrorListSerializer
)

from ..tasks import run_simulation_task
from ..services.simulation_job_service import SimulationJobService
from ..services.simulated_variant_service import SimulatedVariantService
from ..services.simulation_error_service import SimulationErrorService

logger = logging.getLogger(__name__)


class SimulationJobViewSet(viewsets.ModelViewSet):
    """
    Simülasyon işlerini yönetmek için API endpoint'leri.
    """
    queryset = SimulationJob.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'brand__name', 'product_group__name', 'category__name', 'product_model__name']
    ordering_fields = ['name', 'created_at', 'status', 'start_time']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return SimulationJobCreateSerializer
        elif self.action == 'list':
            return SimulationJobListSerializer
        elif self.action == 'retrieve' or self.action == 'update':
            return SimulationJobDetailSerializer
        elif self.action == 'status':
            return SimulationStatusSerializer
        return SimulationJobDetailSerializer

    def get_queryset(self):
        """Filtrelenmis queryset doner"""
        queryset = super().get_queryset()
        
        # Level'e göre filtrele
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Duruma göre filtrele
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Tarih aralığına göre filtrele
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        
        # Sadece aktif simülasyonları göster (aksi belirtilmedikçe)
        show_inactive = self.request.query_params.get('show_inactive', 'false').lower() == 'true'
        if not show_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Yeni bir simülasyon oluşturur"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        simulation = serializer.save()
        
        # Detay serializer ile yanıt döndür
        detail_serializer = SimulationJobDetailSerializer(simulation, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Simülasyonu ve ilişkili varyantları/hataları siler"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": f"Simülasyon #{instance.id} ve ilişkili tüm veriler başarıyla silindi."}, 
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Simülasyon durumunu kontrol etmek için endpoint"""
        instance = self.get_object()
        serializer = SimulationStatusSerializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Bekleyen veya başarısız bir simülasyonu başlatır"""
        instance = self.get_object()
        
        if instance.status not in [SimulationJob.SimulationStatus.PENDING, 
                                  SimulationJob.SimulationStatus.FAILED,
                                  SimulationJob.SimulationStatus.CANCELLED]:
            return Response(
                {"error": f"Simülasyon zaten {instance.get_status_display()} durumunda."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Celery görevi başlat
        task = run_simulation_task.delay(
            simulation_id=instance.id,
            parallel=True,
            max_workers=4
        )
        
        # Simülasyon bilgilerini güncelle
        instance.celery_task_id = task.id
        instance.status = SimulationJob.SimulationStatus.RUNNING
        instance.start_time = datetime.now()
        instance.save()
        
        return Response({
            "message": f"Simülasyon #{instance.id} başlatıldı.",
            "task_id": task.id
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Çalışan bir simülasyonu iptal eder"""
        instance = self.get_object()
        
        if instance.status != SimulationJob.SimulationStatus.RUNNING:
            return Response(
                {"error": f"Simülasyon {instance.get_status_display()} durumunda, sadece çalışan simülasyonlar iptal edilebilir."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Celery görevini iptal et
        if instance.celery_task_id:
            from celery.result import AsyncResult
            task_result = AsyncResult(instance.celery_task_id)
            task_result.revoke(terminate=True)
        
        # Simülasyon durumunu güncelle
        instance.status = SimulationJob.SimulationStatus.CANCELLED
        instance.save()
        
        return Response({
            "message": f"Simülasyon #{instance.id} iptal edildi."
        })

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Simülasyona ait varyantları listeler"""
        instance = self.get_object()
        
        # Sayfalama parametreleri
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        
        # Filtreleme parametreleri
        product_model_id = request.query_params.get('product_model_id')
        variant_code = request.query_params.get('variant_code')
        
        # Varyantları getir
        service = SimulatedVariantService()
        variants = service.get_variants_by_simulation(instance.id)
        
        # Filtreleme
        if product_model_id:
            variants = variants.filter(product_model_id=product_model_id)
        if variant_code:
            variants = variants.filter(variant_code__icontains=variant_code)
        
        # Sayfalama
        start = (page - 1) * page_size
        end = start + page_size
        paginated_variants = variants[start:end]
        
        # Serileştir
        serializer = SimulatedVariantListSerializer(paginated_variants, many=True)
        
        return Response({
            'count': variants.count(),
            'page': page,
            'page_size': page_size,
            'total_pages': (variants.count() + page_size - 1) // page_size,
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def errors(self, request, pk=None):
        """Simülasyona ait hataları listeler"""
        instance = self.get_object()
        
        # Sayfalama parametreleri
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        
        # Filtreleme parametreleri
        error_type = request.query_params.get('error_type')
        severity = request.query_params.get('severity')
        resolution_status = request.query_params.get('resolution_status')
        
        # Ürün modeliyle ilgili hataları filtrele
        product_model_id = request.query_params.get('product_model_id')
        
        # Hataları getir
        service = SimulationErrorService()
        errors = service.get_errors_by_simulation(instance.id)
        
        # Filtreleme
        if error_type:
            errors = errors.filter(error_type=error_type)
        if severity:
            errors = errors.filter(severity=severity)
        if resolution_status is not None:
            errors = errors.filter(resolution_status=resolution_status.lower() == 'true')
        if product_model_id:
            errors = errors.filter(product_model_id=product_model_id)
        
        # Sayfalama
        start = (page - 1) * page_size
        end = start + page_size
        paginated_errors = errors[start:end]
        
        # Serileştir
        serializer = SimulationErrorListSerializer(paginated_errors, many=True)
        
        return Response({
            'count': errors.count(),
            'page': page,
            'page_size': page_size,
            'total_pages': (errors.count() + page_size - 1) // page_size,
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Simülasyon sonuçlarının özeti"""
        instance = self.get_object()
        
        # Servis üzerinden istatistikleri al
        variant_service = SimulatedVariantService()
        error_service = SimulationErrorService()
        
        variant_stats = variant_service.get_variant_statistics(instance.id)
        error_stats = error_service.get_error_statistics(instance.id)
        
        # Özet bilgileri hazırla
        summary = {
            'simulation': {
                'id': instance.id,
                'name': instance.name,
                'status': instance.status,
                'status_display': instance.get_status_display(),
                'level': instance.level,
                'level_display': instance.get_level_display(),
                'start_time': instance.start_time,
                'end_time': instance.end_time,
                'duration': (instance.end_time - instance.start_time).total_seconds() if instance.start_time and instance.end_time else None,
            },
            'stats': {
                'total_models': instance.total_models,
                'processed_models': instance.processed_models,
                'total_variants': variant_stats['total_count'],
                'total_errors': error_stats['total_count'],
                'variant_price_info': variant_stats['price_info'],
                'errors_by_type': error_stats['by_type'],
                'errors_by_severity': error_stats['by_severity'],
                'errors_resolution': error_stats['resolution_stats'],
            },
            'models': variant_stats['by_product_model']
        }
        
        return Response(summary)

    @action(detail=True, methods=['get'])
    def export_variants(self, request, pk=None):
        """Varyantları CSV veya JSON formatında dışa aktarır"""
        instance = self.get_object()
        format_type = request.query_params.get('format', 'csv').lower()
        
        # Servis üzerinden varyantları al
        service = SimulatedVariantService()
        variants = service.get_variants_by_simulation(instance.id)
        
        # Ürün modeline göre filtreleme (opsiyonel)
        product_model_id = request.query_params.get('product_model_id')
        if product_model_id:
            variants = variants.filter(product_model_id=product_model_id)
        
        # Dışa aktarılacak alan isimleri
        fieldnames = ['id', 'product_model_name', 'variant_code', 'variant_description', 
                     'total_price', 'old_component_codes', 'created_at_formatted']
        
        # Dosya adı
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"simulation_{instance.id}_variants_{timestamp}"
        
        # CSV formatı
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            
            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()
            
            serializer = SimulatedVariantExportSerializer(variants, many=True)
            for row in serializer.data:
                # old_component_codes listesini string'e dönüştür
                if isinstance(row['old_component_codes'], list):
                    row['old_component_codes'] = ', '.join(row['old_component_codes'])
                writer.writerow(row)
            
            return response
        
        # JSON formatı
        elif format_type == 'json':
            serializer = SimulatedVariantExportSerializer(variants, many=True)
            json_data = json.dumps(serializer.data, ensure_ascii=False, indent=2)
            
            response = HttpResponse(json_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
            return response
        
        # Desteklenmeyen format
        else:
            return Response(
                {"error": f"Desteklenmeyen format: {format_type}. Desteklenen formatlar: csv, json"},
                status=status.HTTP_400_BAD_REQUEST
            )