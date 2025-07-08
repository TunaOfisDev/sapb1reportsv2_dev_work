# backend/productconfig_simulator/api/simulation_error_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

import logging

from ..models.simulation_error import SimulationError
from ..serializers import (
    SimulationErrorSerializer,
    SimulationErrorDetailSerializer,
    SimulationErrorListSerializer,
    SimulationErrorResolveSerializer,
    SimulationErrorBulkResolveSerializer
)

from ..services.simulation_error_service import SimulationErrorService

logger = logging.getLogger(__name__)

class SimulationErrorViewSet(viewsets.ModelViewSet):
    """
    Simülasyon hataları için API endpoint'leri.
    """
    queryset = SimulationError.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message', 'product_model__name', 'question__name', 'option__name']
    ordering_fields = ['created_at', 'error_type', 'severity', 'resolution_status']
    ordering = ['-created_at']
    http_method_names = ['get', 'put', 'patch', 'head', 'options']  # POST ve DELETE yok

    def get_serializer_class(self):
        if self.action == 'list':
            return SimulationErrorListSerializer
        elif self.action == 'retrieve':
            return SimulationErrorDetailSerializer
        elif self.action == 'resolve' or self.action == 'partial_update' or self.action == 'update':
            return SimulationErrorResolveSerializer
        elif self.action == 'bulk_resolve':
            return SimulationErrorBulkResolveSerializer
        return SimulationErrorSerializer

    def get_queryset(self):
        """Filtrelenmiş queryset döner"""
        queryset = super().get_queryset()
        
        # Simülasyona göre filtrele
        simulation_id = self.request.query_params.get('simulation_id')
        if simulation_id:
            queryset = queryset.filter(simulation_id=simulation_id)
        
        # Hata türüne göre filtrele
        error_type = self.request.query_params.get('error_type')
        if error_type:
            queryset = queryset.filter(error_type=error_type)
        
        # Önem derecesine göre filtrele
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Çözüm durumuna göre filtrele
        resolution_status = self.request.query_params.get('resolution_status')
        if resolution_status is not None:
            queryset = queryset.filter(resolution_status=resolution_status.lower() == 'true')
        
        # Ürün modeline göre filtrele
        product_model_id = self.request.query_params.get('product_model_id')
        if product_model_id:
            queryset = queryset.filter(product_model_id=product_model_id)
        
        # Soruya göre filtrele
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        
        return queryset

    @action(detail=True, methods=['patch', 'put'])
    def resolve(self, request, pk=None):
        """Bir hatayı çözüldü olarak işaretler"""
        instance = self.get_object()
        
        # Zaten çözülmüşse hata döndür
        if instance.resolution_status:
            return Response(
                {"error": "Bu hata zaten çözüldü olarak işaretlenmiş."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SimulationErrorResolveSerializer(
            instance, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Güncellenmiş detayları döndür
        detail_serializer = SimulationErrorDetailSerializer(instance)
        return Response(detail_serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_resolve(self, request):
        """Birden çok hatayı toplu olarak çözüldü işaretler"""
        serializer = SimulationErrorBulkResolveSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response({
            'message': f"{result['resolved_count']} adet hata çözüldü olarak işaretlendi.",
            'resolved_error_ids': result['error_ids']
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Hata istatistiklerini döndürür"""
        # Simülasyon ID'sine göre filtreleme (opsiyonel)
        simulation_id = request.query_params.get('simulation_id')
        
        # Servis üzerinden istatistikleri al
        service = SimulationErrorService()
        stats = service.get_error_statistics(simulation_id)
        
        return Response(stats)
        
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Hata türüne göre hataları gruplar"""
        # Simülasyon ID'sine göre filtreleme (opsiyonel)
        simulation_id = request.query_params.get('simulation_id')
        
        # Hataları getir
        service = SimulationErrorService()
        if simulation_id:
            errors = service.get_errors_by_simulation(simulation_id)
        else:
            errors = service.get_all()
            
        # Hata türlerine göre grup bilgilerini al
        from ..utils.error_helpers import SimulationErrorHelper
        helper = SimulationErrorHelper()
        grouped_errors = helper.group_errors_by_type(errors)
        
        # Sonuç formatını hazırla
        result = {}
        for error_type, errors_list in grouped_errors.items():
            result[error_type] = {
                'count': len(errors_list),
                'severity_counts': {
                    'info': sum(1 for e in errors_list if e.severity == 'info'),
                    'warning': sum(1 for e in errors_list if e.severity == 'warning'),
                    'error': sum(1 for e in errors_list if e.severity == 'error'),
                    'critical': sum(1 for e in errors_list if e.severity == 'critical'),
                },
                'resolved_count': sum(1 for e in errors_list if e.resolution_status),
                'unresolved_count': sum(1 for e in errors_list if not e.resolution_status),
            }
            
        return Response(result)
        
    @action(detail=False, methods=['get'])
    def by_product_model(self, request):
        """Ürün modeline göre hataları gruplar"""
        # Simülasyon ID'sine göre filtreleme (opsiyonel)
        simulation_id = request.query_params.get('simulation_id')
        
        # Hataları getir
        service = SimulationErrorService()
        if simulation_id:
            errors = service.get_errors_by_simulation(simulation_id)
        else:
            errors = service.get_all()
            
        # Ürün modellerine göre grup bilgilerini al
        from ..utils.error_helpers import SimulationErrorHelper
        helper = SimulationErrorHelper()
        grouped_errors = helper.group_errors_by_product_model(errors)
        
        # Sonuç formatını hazırla
        result = {}
        for key, errors_list in grouped_errors.items():
            # key formatı: "model_id-model_name" veya "no_product_model"
            if key == "no_product_model":
                model_info = {"id": None, "name": "Ürün Modeli Yok"}
            else:
                model_id, model_name = key.split('-', 1)
                model_info = {"id": int(model_id), "name": model_name}
                
            result[key] = {
                'model': model_info,
                'count': len(errors_list),
                'error_types': {
                    error_type: sum(1 for e in errors_list if e.error_type == error_type)
                    for error_type in set(e.error_type for e in errors_list)
                },
                'resolved_count': sum(1 for e in errors_list if e.resolution_status),
                'unresolved_count': sum(1 for e in errors_list if not e.resolution_status),
                'severity_counts': {
                    'info': sum(1 for e in errors_list if e.severity == 'info'),
                    'warning': sum(1 for e in errors_list if e.severity == 'warning'),
                    'error': sum(1 for e in errors_list if e.severity == 'error'),
                    'critical': sum(1 for e in errors_list if e.severity == 'critical'),
                }
            }
            
        return Response(result)
        
    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Önem derecesine göre hataları gruplar"""
        # Simülasyon ID'sine göre filtreleme (opsiyonel)
        simulation_id = request.query_params.get('simulation_id')
        
        # Hataları getir
        service = SimulationErrorService()
        if simulation_id:
            errors = service.get_errors_by_simulation(simulation_id)
        else:
            errors = service.get_all()
            
        # Önem derecesine göre grup bilgilerini al
        from ..utils.error_helpers import SimulationErrorHelper
        helper = SimulationErrorHelper()
        grouped_errors = helper.group_errors_by_severity(errors)
        
        # Sonuç formatını hazırla
        result = {}
        for severity, errors_list in grouped_errors.items():
            result[severity] = {
                'count': len(errors_list),
                'error_types': {
                    error_type: sum(1 for e in errors_list if e.error_type == error_type)
                    for error_type in set(e.error_type for e in errors_list)
                },
                'resolved_count': sum(1 for e in errors_list if e.resolution_status),
                'unresolved_count': sum(1 for e in errors_list if not e.resolution_status),
            }
            
        return Response(result)
        
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Hata özeti döndürür"""
        # Simülasyon ID'sine göre filtreleme (opsiyonel)
        simulation_id = request.query_params.get('simulation_id')
        
        # Servisi kullanarak özet bilgileri al
        service = SimulationErrorService()
        
        # Özet bilgileri hazırla
        summary = service.get_error_summary(simulation_id)
        
        return Response(summary)