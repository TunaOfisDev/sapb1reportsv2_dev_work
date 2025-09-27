# backend/customercollection/api/combinedservice.py
from django.http import JsonResponse
from rest_framework.views import APIView
from .views import FetchHanaCustomerCollectionDataView
from .closinginvoice_view import CustomerCollectionSimulationView

class CombinedServiceView(APIView):
    def get(self, request, *args, **kwargs):
        # İlk adım olarak HANA DB'den veri çekme işlemini gerçekleştir
        fetch_view = FetchHanaCustomerCollectionDataView()
        fetch_response = fetch_view.get(request)
        if fetch_response.status_code != 200:
            return fetch_response

        # İkinci adım olarak çekilen verileri kullanarak kapama işlemini gerçekleştir
        simulation_view = CustomerCollectionSimulationView()
        simulation_response = simulation_view.get(request)
        return simulation_response

