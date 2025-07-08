# backend/productconfig_simulator/api/simulated_variant_views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import logging

from ..models.simulated_variant import SimulatedVariant
from ..serializers import (
    SimulatedVariantSerializer,
    SimulatedVariantDetailSerializer,
    SimulatedVariantListSerializer,
    SimulatedVariantComparisonSerializer
)

logger = logging.getLogger(__name__)

class SimulatedVariantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Simüle edilmiş varyantlar için salt okunur API endpoint'leri.
    """
    queryset = SimulatedVariant.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['variant_code', 'variant_description', 'product_model__name']
    ordering_fields = ['created_at', 'variant_code', 'total_price']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SimulatedVariantListSerializer
        elif self.action == 'retrieve':
            return SimulatedVariantDetailSerializer
        elif self.action == 'compare':
            return SimulatedVariantComparisonSerializer
        return SimulatedVariantSerializer

    def get_queryset(self):
        """Filtrelenmiş queryset döner"""
        queryset = super().get_queryset()
        
        # Simülasyona göre filtrele
        simulation_id = self.request.query_params.get('simulation_id')
        if simulation_id:
            queryset = queryset.filter(simulation_id=simulation_id)
        
        # Ürün modeline göre filtrele
        product_model_id = self.request.query_params.get('product_model_id')
        if product_model_id:
            queryset = queryset.filter(product_model_id=product_model_id)
        
        # Varyant koduna göre filtrele
        variant_code = self.request.query_params.get('variant_code')
        if variant_code:
            queryset = queryset.filter(variant_code__icontains=variant_code)
        
        # Sadece aktif varyantları göster (aksi belirtilmedikçe)
        show_inactive = self.request.query_params.get('show_inactive', 'false').lower() == 'true'
        if not show_inactive:
            queryset = queryset.filter(is_active=True)
        
        return queryset

    @action(detail=True, methods=['get'])
    def compare(self, request, pk=None):
        """Simüle edilmiş varyantı gerçek varyant ile karşılaştırır"""
        instance = self.get_object()
        comparison = instance.compare_with_actual()
        
        return Response({
            'variant': {
                'id': instance.id,
                'variant_code': instance.variant_code,
                'product_model_name': instance.product_model.name if instance.product_model else None,
                'total_price': float(instance.total_price),
            },
            'comparison_result': comparison
        })
        
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Varyant detaylarını daha kapsamlı görüntüler"""
        instance = self.get_object()
        serializer = SimulatedVariantDetailSerializer(instance)
        
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Varyant istatistiklerini döndürür"""
        # Simülasyon ID'sine göre filtreleme
        simulation_id = request.query_params.get('simulation_id')
        
        if not simulation_id:
            return Response(
                {"error": "Simülasyon ID'si (simulation_id) belirtilmelidir."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        from ..services.simulated_variant_service import SimulatedVariantService
        service = SimulatedVariantService()
        stats = service.get_variant_statistics(simulation_id)
        
        return Response(stats)
        
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Varyantlarda arama yapar"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {"error": "Arama sorgusu (q) belirtilmelidir."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        results = self.get_queryset().filter(
            variant_code__icontains=query
        ) | self.get_queryset().filter(
            variant_description__icontains=query
        ) | self.get_queryset().filter(
            product_model__name__icontains=query
        )
        
        paginator = self.paginator
        page = paginator.paginate_queryset(results, request)
        serializer = SimulatedVariantListSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)