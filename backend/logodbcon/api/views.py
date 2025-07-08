# backend/logodbcon/api/views.py
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.sq_query_model import SQLQuery
from ..utilities.logodb_config import create_connection
import logging

logger = logging.getLogger(__name__)

class SQLQueryListView(APIView):
    def get(self, request):
        sql_queries = SQLQuery.objects.all()
        queries_list = [
            {
                'name': query.name,
                'url': request.build_absolute_uri(reverse('sqlquery-detail-logo', args=[query.name]))
            }
            for query in sql_queries
        ]
        return Response(queries_list, status=status.HTTP_200_OK)

class SQLQueryView(APIView):
    def get(self, request, query_name):
        sql_query_instance = SQLQuery.objects.filter(name=query_name).first()
        if not sql_query_instance:
            return Response({"error": "Sorgu bulunamadı"}, status=status.HTTP_404_NOT_FOUND)

        connection = create_connection()
        if not connection:
            logger.error("Veritabanı bağlantısı kurulamadı.")
            return Response({"error": "Veritabanı bağlantısı kurulamadı"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        formatted_query = sql_query_instance.query
        cursor = connection.cursor()
        try:
            cursor.execute(formatted_query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"SQL sorgusu çalıştırılırken hata: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            cursor.close()
            connection.close()

        return Response(result, status=status.HTTP_200_OK)
