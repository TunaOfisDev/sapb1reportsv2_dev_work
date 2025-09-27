# backend/orderarchive/views/order_archive_view.py
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.order_archive_model import OrderDetail
from ..serializers.order_archive_serializer import OrderDetailSerializer
from ..filters.order_archive_filter import OrderDetailFilter
from ..pagination.order_archive_pagination import OrderArchivePagination
import logging

logger = logging.getLogger(__name__)

class OrderDetailViewSet(ReadOnlyModelViewSet):
    """
    Büyük veri setleri için optimize edilmiş OrderDetail API ViewSet.
    Filtreleme, sıralama ve sayfalama desteklenir.
    """

    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderDetailFilter
    ordering_fields = [
        "order_date",
        "order_number",
        "year",
        "month",
        "customer_code",
        "customer_name",
        "item_code",
        "item_description",
        "document_description"
    ]
    ordering = ["-order_date"]
    pagination_class = OrderArchivePagination
    


    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Gelişmiş arama motoru. Belirli alanlarda veya tüm alanlarda arama yapar.
        """
        from django.db.models import Q, Value, IntegerField, Case, When
        from django.db.models.functions import Greatest

        search_query = request.query_params.get('q', None)
        # Her iki parametre adını da kontrol et
        search_field = request.query_params.get('field') or request.query_params.get('fields', 'all')

        if not search_query:
            return Response({"error": "Arama metni boş olamaz."}, status=400)

        try:
            # Arama alanına göre filtre oluştur
            if search_field == 'all':
                # Tüm alanlarda arama
                filter_query = (
                    Q(customer_code__icontains=search_query) |
                    Q(customer_name__icontains=search_query) |
                    Q(item_code__icontains=search_query) |
                    Q(item_description__icontains=search_query) |
                    Q(order_number__icontains=search_query) |
                    Q(document_description__icontains=search_query) |
                    Q(seller__icontains=search_query) |
                    Q(country__icontains=search_query) |
                    Q(city__icontains=search_query)
                )
            else:
                # Belirli alanda arama
                field_mapping = {
                    'customer_code': 'customer_code__icontains',
                    'customer_name': 'customer_name__icontains',
                    'item_code': 'item_code__icontains',
                    'item_description': 'item_description__icontains',
                    'order_number': 'order_number__icontains',
                    'document_description': 'document_description__icontains',
                    'seller': 'seller__icontains',
                    'country': 'country__icontains',
                    'city': 'city__icontains'
                }

                if search_field not in field_mapping:
                    return Response(
                        {"error": f"Geçersiz arama alanı: {search_field}"},
                        status=400
                    )

                filter_query = Q(**{field_mapping[search_field]: search_query})

            # Alaka düzeyi hesaplama ve sıralama
            queryset = self.get_queryset().filter(filter_query)

            # Seçilen alana göre sıralama
            if search_field != 'all':
                # Tam eşleşenleri öne çıkar
                exact_field = field_mapping[search_field].replace('__icontains', '__iexact')
                queryset = queryset.annotate(
                    exact_match=Case(
                        When(**{exact_field: search_query}, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by('-exact_match', '-order_date')
            else:
                # Genel aramada alaka düzeyine göre sırala
                queryset = queryset.annotate(
                    relevance=Greatest(
                        Case(
                            When(customer_name__iexact=search_query, then=Value(100)),
                            When(customer_code__iexact=search_query, then=Value(100)),
                            When(item_code__iexact=search_query, then=Value(100)),
                            When(order_number__iexact=search_query, then=Value(100)),
                            When(country__iexact=search_query, then=Value(100)),
                            When(city__iexact=search_query, then=Value(100)),
                            default=Value(0),
                            output_field=IntegerField(),
                        ),
                        Case(
                            When(customer_name__istartswith=search_query, then=Value(75)),
                            When(customer_code__istartswith=search_query, then=Value(75)),
                            When(item_code__istartswith=search_query, then=Value(75)),
                            When(order_number__istartswith=search_query, then=Value(75)),
                            When(country__istartswith=search_query, then=Value(75)),
                            When(city__istartswith=search_query, then=Value(75)),
                            default=Value(0),
                            output_field=IntegerField(),
                        )
                    )
                ).order_by('-relevance', '-order_date')

            # Debug için loglama
            logger.debug(f"Arama alanı: {search_field}, Sorgu: {search_query}")
            logger.debug(f"Bulunan kayıt sayısı: {queryset.count()}")

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Arama hatası: {str(e)}")
            return Response(
                {"error": f"Arama işlemi sırasında bir hata oluştu: {str(e)}"},
                status=500
            )





    @action(detail=False, methods=['get'], url_path='year-filter', url_name='year-filter')
    def year_filter(self, request):
        """
        Yıl bazında filtreleme ve sıralama yapar.
        """
        try:
            year = request.query_params.get('year')
            ordering = request.query_params.get('ordering', '-order_date')  # Sıralama kriteri (default: order_date DESC)

            if not year:
                return Response({"error": "Yıl parametresi gereklidir."}, status=400)

            year_value = int(year)
            logger.debug(f"Yıl filtresi uygulanıyor: {year_value}, Sıralama: {ordering}")

            # Filtreleme uygula
            queryset = self.get_queryset().filter(
                year=year_value,
                year__isnull=False
            ).order_by(ordering)

            # Kayıt sayısını logla
            record_count = queryset.count()
            logger.debug(f"Bulunan kayıt sayısı: {record_count}")

            # Sayfalama
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except ValueError:
            logger.error(f"Geçersiz yıl formatı: {year}")
            return Response({"error": "Geçersiz yıl formatı"}, status=400)
        except Exception as e:
            logger.error(f"Yıl filtreleme hatası: {str(e)}")
            return Response({"error": str(e)}, status=500)
