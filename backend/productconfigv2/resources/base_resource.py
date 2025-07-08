# backend/productconfigv2/resources/base_resource.py

from import_export import resources
from import_export.results import RowResult
from django.utils import timezone

class BaseResource(resources.ModelResource):
    """
    Ortak işlevleri sağlayan soyut resource sınıfı.
    - Soft delete desteği
    - created_by / updated_by ataması
    - Veri temizliği ve analiz logları
    """

    def before_import_row(self, row, **kwargs):
        request = kwargs.get("user")
        now = timezone.now()

        if "created_at" in self.fields:
            row["created_at"] = row.get("created_at", now)
        if "updated_at" in self.fields:
            row["updated_at"] = now

        if "created_by" in self.fields and request:
            row["created_by"] = request
        if "updated_by" in self.fields and request:
            row["updated_by"] = request

        # Örn: boşluk temizliği
        for key in row.keys():
            if isinstance(row[key], str):
                row[key] = row[key].strip()

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if hasattr(instance, "is_active") and not instance.is_active:
            return True  # pasif kayıtları atla
        return super().skip_row(instance, original, row, import_validation_errors)

    # Burada eklenen fields parametresi
    def get_export_headers(self, fields=None):
        headers = super().get_export_headers(fields=fields)
        return [header.upper() for header in headers]

    def get_row_result_class(self):
        return RowResult

