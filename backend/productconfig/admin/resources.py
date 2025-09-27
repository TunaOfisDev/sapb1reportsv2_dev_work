# backend/productconfig/admin/resources.py
from import_export import resources
from django.apps import apps

class GenericResource(resources.ModelResource):
    """
    Tüm modeller için geçerli olacak genel kaynak sınıfı.
    Dinamik olarak model atanır.
    """

    def __init__(self, model_name=None, *args, **kwargs):
        if model_name:
            self._meta.model = apps.get_model('productconfig', model_name)
        super().__init__(*args, **kwargs)

    class Meta:
        model = None  # Model daha sonra dinamik olarak atanacak
