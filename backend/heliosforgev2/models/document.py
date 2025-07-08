# backend/heliosforgev2/models/document.py

import os
from django.db import models
from django.conf import settings
from django.utils.timezone import now

def get_pdf_upload_path(instance, filename):
    """
    PDF dosyasını heliosforgev2/storage/pdf/ altına kaydeder.
    """
    today = now().strftime("%Y%m%d")
    return os.path.relpath(
        os.path.join(settings.HELIOS_STORAGE["PDF"], f"{today}_{filename}"),
        settings.MEDIA_ROOT
    )

class Document(models.Model):
    """
    Sisteme yüklenen PDF dosyalarını temsil eder. Dosya fiziksel olarak 'heliosforgev2/storage/pdf/' altında tutulur.
    """
    id = models.AutoField(primary_key=True)
    file = models.FileField(
        upload_to=get_pdf_upload_path,
        help_text="Yüklenen PDF dosyası"
    )
    page_count = models.PositiveIntegerField(default=0, help_text="PDF içindeki toplam sayfa")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("parsed", "Parsed"),
            ("error", "Error"),
        ],
        default="pending"
    )

    def __str__(self):
        return self.file.name.split("/")[-1]

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-uploaded_at"]
