# backend/hanadbcon/api/views.py
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#from rest_framework.permissions import IsAuthenticated
#from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models.sq_query_model import SQLQuery
from ..utilities.hanadb_config import create_connection
from django.conf import settings

class SQLQueryListView(APIView):

    def get(self, request):
        # Tüm SQLQuery objelerini al
        sql_queries = SQLQuery.objects.all()
        # Her bir sorgu için isim ve URL oluştur
        queries_list = [
            {
                'name': query.name,
                'url': request.build_absolute_uri(reverse('sqlquery-detail-hana', args=[query.name]))
            }
            for query in sql_queries
        ]
        return Response(queries_list, status=status.HTTP_200_OK)

class SQLQueryView(APIView):
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]

    def get(self, request, query_name):
        # SQL sorgusunu adına göre bulma
        sql_query_instance = SQLQuery.objects.filter(name=query_name).first()
        if not sql_query_instance:
            return Response({"error": "Sorgu bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

        # HANA DB bağlantısı
        connection = create_connection()
        if not connection:
            return Response({"error": "Veritabanı bağlantısı kurulamadı"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Schema parametresini al, eğer yoksa settings.py'daki varsayılan değeri kullan
        schema = request.query_params.get('schema', settings.HANADB_SCHEMA)
        
        # Sorgu için parametreleri al
        parameters = []
        if sql_query_instance.parameters:
            for param in sql_query_instance.parameters:
                param_value = request.query_params.get(param['name'])
                if not param_value:
                    return Response({"error": f"{param['name']} parametresi eksik"}, status=status.HTTP_400_BAD_REQUEST)
                parameters.append(param_value)

        # SQL sorgusunu formatlama
        formatted_query = sql_query_instance.query.replace("{schema}", schema)

        cursor = connection.cursor()
        try:
            # Parametreleri güvenli şekilde SQL sorgusuna bağla
            cursor.execute(formatted_query, parameters)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            cursor.close()
            connection.close()

        return Response(result, status=status.HTTP_200_OK)


