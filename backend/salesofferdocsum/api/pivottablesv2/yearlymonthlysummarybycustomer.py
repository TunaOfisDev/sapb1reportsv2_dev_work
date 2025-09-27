# backend/salesofferdocsum/api/pivottablesv2/yearlymonthlysummarybycustomer.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...utilities.pivottablesv2.yearlymonthlysummarybycustomer_data_fetcher import fetch_yearly_monthly_summary_by_customer_data # type: ignore

class YearlyMonthlySummaryByCustomerView(APIView):
    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return Response({"error": "Authorization token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Token'dan 'Bearer ' kısmını çıkarıyoruz
        token = token.replace('Bearer ', '')

        try:
            summary_data = fetch_yearly_monthly_summary_by_customer_data(token)
            return Response(summary_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

