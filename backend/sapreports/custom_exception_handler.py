# backend/sapreports/custom_exception_handler.py
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict):
            response.data['status_code'] = response.status_code
        elif isinstance(response.data, list):  # Eğer bir liste ise
            for index, item in enumerate(response.data):  # enumerate kullanılarak index değeri alınır
                if isinstance(item, dict):
                    response.data[index]['status_code'] = response.status_code  # index kullanılarak listeye erişilir
    return response