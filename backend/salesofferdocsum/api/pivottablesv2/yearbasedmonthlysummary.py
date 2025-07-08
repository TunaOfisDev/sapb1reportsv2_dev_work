# backend/salesofferdocsum/api/pivottablesv2/yearbasedmonthlysummary.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...utilities.pivottablesv2.yearbasedmonthlysummary_data_fetcher import fetch_year_based_monthly_summary_data # type: ignore

class YearBasedMonthlySummaryView(APIView):
    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return Response({"error": "Authorization token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Token'dan 'Bearer ' kısmını çıkarıyoruz
        token = token.replace('Bearer ', '')

        try:
            summary_data = fetch_year_based_monthly_summary_data(token)
            return Response(summary_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
