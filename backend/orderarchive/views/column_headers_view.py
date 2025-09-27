# backend/orderarchive/views/column_headers_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models.order_archive_model import OrderDetail

class ColumnHeadersAPIView(APIView):
    """
    Dinamik kolon başlıklarını ve veri tiplerini dönen API.
    """

    def get(self, request, *args, **kwargs):
        # Modeldeki alanları döngüyle okuyarak başlık ve veri tipi bilgilerini oluştur
        headers = [
            {
                "name": field.name,  # Alan adı (backend'deki modeldeki İngilizce ad)
                "verbose_name": field.verbose_name,  # Türkçe başlık adı
                "type": self.get_field_type(field)  # Veri tipi
            }
            for field in OrderDetail._meta.get_fields()
            if field.concrete  # Sadece gerçek alanları dikkate al (ManyToMany vs. hariç)
        ]

        return Response(headers)

    def get_field_type(self, field):
        django_field_type_to_json = {
            "CharField": "string",
            "TextField": "string",
            "IntegerField": "integer",
            "DecimalField": "float",
            "DateField": "date",
            "DateTimeField": "datetime",
            "BooleanField": "boolean",
            "FloatField": "float",
            "AutoField": "integer",
            "BigAutoField": "integer",
        }
        field_type = field.get_internal_type()
        if field_type not in django_field_type_to_json:
            print(f"Unknown field type: {field_type}")  # Loglama
        return django_field_type_to_json.get(field_type, "unknown")

