# productconfigv2/api/views/specification_views.py

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from ...models import (
    SpecificationType, SpecOption,
    ProductSpecification, SpecificationOption
)
from ..serializers import (
    SpecificationTypeSerializer, SpecOptionSerializer,
    ProductSpecificationSerializer, SpecificationOptionSerializer
)


class SpecificationTypeViewSet(viewsets.ModelViewSet):
    queryset = SpecificationType.objects.all()
    serializer_class = SpecificationTypeSerializer


class SpecOptionViewSet(viewsets.ModelViewSet):
    queryset = SpecOption.objects.all()
    serializer_class = SpecOptionSerializer

    @action(detail=False, methods=['GET'])
    def by_spec_type(self, request):
        spec_type_id = request.query_params.get('spec_type')
        if not spec_type_id:
            return Response({"error": "spec_type parametresi gerekli"}, status=400)
        
        queryset = SpecOption.objects.filter(spec_type_id=spec_type_id, is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductSpecificationViewSet(viewsets.ModelViewSet):
    queryset = ProductSpecification.objects.all()
    serializer_class = ProductSpecificationSerializer


class SpecificationOptionViewSet(viewsets.ModelViewSet):
    queryset = SpecificationOption.objects.all()
    serializer_class = SpecificationOptionSerializer
