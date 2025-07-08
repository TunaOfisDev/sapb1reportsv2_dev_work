# backend\dynamicreport\views.py
from rest_framework import generics
from rest_framework import viewsets
from ..models.models import SqlQuery, DynamicTable, DynamicHeaders, HanaDataType
from ..serializers import SqlQuerySerializer, DynamicTableSerializer, DynamicHeadersSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..utilities.hana_services import execute_hana_sql_query 
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.admin import site
from ..admin import SqlQueryAdmin
from ..models.models import SqlQuery
import json
import re

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sql_query_list(request):
    try:
        sql_queries = SqlQuery.objects.all()
        serializer = SqlQuerySerializer(sql_queries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_and_generate_report(request):
    try:
        # SQL sorgusu ID'lerini al
        sql_query_ids = request.data.get('sql_query_ids', [])
        queryset = SqlQuery.objects.filter(id__in=sql_query_ids)

        # Admin aksiyonunu çağır
        admin_view = SqlQueryAdmin(SqlQuery, site)
        admin_view.test_and_generate_report(request, queryset)
        
        return Response({"status": "success", "message": "SQL sorguları başarıyla çalıştırıldı ve rapor oluşturuldu."})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # İzni buraya ekleyin
def get_joined_headers_types_class(request):
    try:
        # Join the tables and select the necessary columns
        joined_data = DynamicHeaders.objects.select_related('type').values(
            dynamic_table_name=F('dynamic_table__table_name'),  # Alias here
            column_name=F('header_name'),
            type_class=F('type__type_class')
        )

        # Convert QuerySet to list
        joined_data_list = list(joined_data)
        
        return JsonResponse({"status": "success", "data": joined_data_list}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# hana data tipleri al
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_hana_data_types(request):
    try:
        hana_types = HanaDataType.objects.values('type_code', 'type_class')
        return JsonResponse({"status": "success", "data": list(hana_types)}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# DynamicTable view set'i
class DynamicTableViewSet(viewsets.ModelViewSet):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer
    permission_classes = [IsAuthenticated]  # İzni buraya ekleyin

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {}
        if 'pk' in self.kwargs:
            filter_kwargs['id'] = self.kwargs['pk']
        elif 'table_name' in self.kwargs:
            filter_kwargs['table_name'] = self.kwargs['table_name']
        obj = get_object_or_404(queryset, **filter_kwargs)
        return obj

    def retrieve_by_name(self, request, table_name=None):
        queryset = DynamicTable.objects.filter(table_name=table_name)
        if not queryset.exists():
            return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DynamicTableSerializer(queryset.first())
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'], url_path='check_column_types')
    def check_column_types(self, request, table_name=None, pk=None):
        if table_name is None:
            return Response({"error": "Table name must be provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        selected_columns = request.data.get('selected_columns', [])
        if not selected_columns:
            return Response({"error": "No columns selected."}, status=status.HTTP_400_BAD_REQUEST)

        # Kolonların DynamicHeaders modelinde tanımlı olup olmadığını kontrol et
        table = DynamicTable.objects.filter(table_name=table_name).first()
        if table is None:
            return Response({"error": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        dynamic_headers = DynamicHeaders.objects.filter(dynamic_table=table, header_name__in=selected_columns)
        if len(dynamic_headers) != len(selected_columns):
            return Response({"error": "Some selected columns are not defined in DynamicHeaders."}, status=status.HTTP_400_BAD_REQUEST)

        # Kolon tipini kontrol et
        for dynamic_header in dynamic_headers:
            if dynamic_header.type not in ['integer', 'double', 'decimal']:  # Sayısal tipler
                raise ValidationError(f"The column {dynamic_header.header_name} is not of a numeric type suitable for graphing.")
        
        return Response({"message": "All selected columns are suitable for graphing."}, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['GET'], url_path='fetch_local_data_with_alignment/(?P<table_name>[^/.]+)')
    def fetch_local_data_with_alignment(self, request, table_name=None, pk=None):
        queryset = DynamicTable.objects.filter(table_name=table_name)
        if not queryset.exists():
            return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)
        
        data = queryset.first().hana_data_set  
        first_row = data[0] if isinstance(data, list) else json.loads(data)[0]

        # Sayı, nokta ve virgül içeren hücreleri belirlemek için regex
        pattern = re.compile(r'^\d{1,3}(?:,\d{3})*(\.\d+)?(?:,\d+)?$')

        # Sayısal verilerin indexlerini saklayacak listemiz
        index_list = [i for i, cell in enumerate(first_row) if pattern.fullmatch(str(cell))]

        # İndex listemizi ve ilk satırın bir örneğini frontend'e gönderiyoruz
        return JsonResponse({'alignment_indexes': index_list, 'first_row_example': first_row}, safe=False, json_dumps_params={'ensure_ascii': False})


@api_view(['GET'])
def sql_table_list(request):
    try:
        # Tüm SQL tablo isimlerini al
        sql_table_names = SqlQuery.objects.values_list('table_name', flat=True).distinct()
        return Response(sql_table_names, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'DELETE'])
def sql_query_detail_by_name(request, table_name):
    try:
        sql_query = SqlQuery.objects.get(table_name=table_name)
    except SqlQuery.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SqlQuerySerializer(sql_query)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SqlQuerySerializer(sql_query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sql_query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'PUT', 'DELETE'])
def sql_query_detail_by_id(request, pk):
    try:
        sql_query = SqlQuery.objects.get(pk=pk)
    except SqlQuery.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SqlQuerySerializer(sql_query)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SqlQuerySerializer(sql_query, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sql_query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def fetch_instant_data_by_name(request, table_name):
    try:
        sql_query_obj = SqlQuery.objects.get(table_name=table_name)
        sql_query = sql_query_obj.query
        
        # HANA servisini çağırarak veriyi çek
        result = execute_hana_sql_query(sql_query, table_name)
        
        # HANA'dan dönen sonuç zaten bir liste olduğu için, direkt olarak dönebiliriz
        return Response(result, status=status.HTTP_200_OK)
        
    except SqlQuery.DoesNotExist:
        return Response({"error": "SQL sorgusu bulunamadı"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET', 'PUT', 'DELETE'])
def dynamic_headers_detail_by_id(request, pk):
    try:
        dynamic_headers = DynamicHeaders.objects.get(pk=pk)
    except DynamicHeaders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DynamicHeadersSerializer(dynamic_headers)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DynamicHeadersSerializer(dynamic_headers, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        dynamic_headers.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# DynamicHeaders için özel bir view oluşturun
class DynamicHeadersByTable(APIView):
    def get(self, request, table_name):
        # Tablo adına göre başlıkları filtreleyin
        dynamic_headers = DynamicHeaders.objects.filter(table_name=table_name)

        # Eğer hiç sonuç yoksa, 404 döndür
        if not dynamic_headers.exists():
            return Response({"detail": "Bulunamadı.", "status_code": 404}, status=status.HTTP_404_NOT_FOUND)

        # Sonuçları serialize edin
        serializer = DynamicHeadersSerializer(dynamic_headers, many=True)
        
        # JSON yanıtını döndür
        return Response(serializer.data)


# SqlQuery view set'i
class SqlQueryViewSet(viewsets.ModelViewSet):
    queryset = SqlQuery.objects.all()
    serializer_class = SqlQuerySerializer

    @action(detail=False, methods=['GET'], url_path='sys-table-columns/(?P<table_name>[^/.]+)')
    def get_sys_table_columns(self, request, table_name=None):
        try:
            sql_query = SqlQuery.objects.get(table_name=table_name)
        except SqlQuery.DoesNotExist:
            return Response({"error": "Table not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"sys_table_columns": sql_query.sys_table_columns}, status=status.HTTP_200_OK)


# DynamicHeaders view set'i
class DynamicHeadersViewSet(viewsets.ModelViewSet):
    queryset = DynamicHeaders.objects.all()
    serializer_class = DynamicHeadersSerializer

# API görünümlerini oluşturun
@api_view(['GET', 'POST'])
def sql_query_list_create(request):
    if request.method == 'GET':
        sql_queries = SqlQuery.objects.all()
        serializer = SqlQuerySerializer(sql_queries, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SqlQuerySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def dynamic_table_detail(request, pk):
    try:
        dynamic_table = DynamicTable.objects.get(pk=pk)
    except DynamicTable.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DynamicTableSerializer(dynamic_table)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DynamicTableSerializer(dynamic_table, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        dynamic_table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'PUT', 'DELETE'])
def dynamic_headers_detail(request, pk):
    try:
        dynamic_headers = DynamicHeaders.objects.get(pk=pk)
    except DynamicHeaders.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DynamicHeadersSerializer(dynamic_headers)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DynamicHeadersSerializer(dynamic_headers, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        dynamic_headers.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SqlQueryListCreateView(generics.ListCreateAPIView):
    queryset = SqlQuery.objects.all()
    serializer_class = SqlQuerySerializer

class SqlQueryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SqlQuery.objects.all()
    serializer_class = SqlQuerySerializer

class DynamicTableListCreateView(generics.ListCreateAPIView):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer

class DynamicTableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer

class DynamicHeadersListCreateView(generics.ListCreateAPIView):
    queryset = DynamicHeaders.objects.all()
    serializer_class = DynamicHeadersSerializer

class DynamicHeadersDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DynamicHeaders.objects.all()
    serializer_class = DynamicHeadersSerializer

