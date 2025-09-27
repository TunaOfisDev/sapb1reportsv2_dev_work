# backend/shipweekplanner/api/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from ..serializers import ShipmentOrderSerializer
from ..models.models import ShipmentOrder
from ..utils.date_utils import (
    get_week_range, 
    copy_to_next_week, 
    get_current_week, 
    generate_weekly_report
)

class ShipmentOrderViewSet(viewsets.ModelViewSet):
    """
    CRUD işlemleri ve ek özel işlemlerle sevkiyat siparişleri için API endpoint.
    """
    queryset = ShipmentOrder.objects.all()
    serializer_class = ShipmentOrderSerializer

    def list(self, request, *args, **kwargs):
        """Sevkiyat siparişlerini listele."""
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Belirli bir sevkiyat siparişini getir."""
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Yeni bir sevkiyat siparişi oluştur."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """Var olan bir sevkiyat siparişini güncelle."""
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """Bir sevkiyat siparişini sil."""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def weekly_orders(self, request):
        """Haftalık sevk siparişlerini getir."""
        week_number = request.query_params.get('week', timezone.now().isocalendar()[1])
        year = request.query_params.get('year', timezone.now().year)

        start_of_week, end_of_week = get_week_range(int(year), int(week_number))
        orders = ShipmentOrder.objects.filter(shipment_date__range=(start_of_week, end_of_week))

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def copy_next_week(self, request):
        """SevkTarih alanı boş olan siparişleri bir sonraki haftaya kopyalar."""
        current_week = get_current_week()
        shipment_orders = ShipmentOrder.objects.filter(shipment_date__range=(current_week[0], current_week[1]))

        copied_orders = copy_to_next_week(shipment_orders, current_week)

        serializer = self.get_serializer(copied_orders, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def weekly_report(self, request):
        """Belirtilen hafta için haftalık sevk raporunu döner."""
        week_number = int(request.query_params.get('week', timezone.now().isocalendar()[1]))
        year = int(request.query_params.get('year', timezone.now().year))

        report = generate_weekly_report(year, week_number)
        return Response(report, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def current_week(self, request):
        """Geçerli haftanın sevk siparişlerini döner."""
        current_week = get_current_week()
        orders = ShipmentOrder.objects.filter(shipment_date__range=(current_week[0], current_week[1]))

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)