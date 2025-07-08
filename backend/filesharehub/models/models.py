# backend/filesharehub/models/models.py
from django.db import models
from django.utils import timezone
from .base import BaseModel
from ..tasks import scan_directory_task  # Celery görevini import edin

SHARE_PATH = "/mnt/gorseller"

class Directory(BaseModel):
    """
    Paylaşılan dizin bilgilerini içerir.
    """
    path = models.CharField(max_length=500, unique=True)
    last_scanned = models.DateTimeField(null=True)

    def __str__(self):
        return self.path

    @staticmethod
    def get_default_directory():
        """
        Varsayılan dizini döndürür.
        """
        return SHARE_PATH

    @staticmethod
    def get_or_create_directory(path):
        """
        Dizin yoksa oluşturur ve döner.
        """
        directory, created = Directory.objects.get_or_create(path=path)
        return directory

    def needs_scan(self):
        """
        Dizin yeniden taranmalı mı kontrol eder.
        Örneğin, son tarama 1 saatten eskiyse taranmalı.
        """
        if self.last_scanned is None:
            return True
        return (timezone.now() - self.last_scanned).total_seconds() > 36000  # 10 saat

    def trigger_scan(self):
        """
        Dizini taramak için bir arka plan görevi başlatır.
        """
        scan_directory_task.delay(self.path)


class FileRecord(BaseModel):
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, related_name='files', default=1)
    size = models.BigIntegerField(default=0)  # Dosya boyutu (byte cinsinden)
    last_modified = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('directory', 'filename')
        permissions = [
            ("read_file", "Can read file"),
            ("download_file", "Can download file"),
        ]

    def __str__(self):
        return self.filename

    @staticmethod
    def list_files_in_directory(directory_path=None):
        """
        Belirtilen dizindeki dosyaların listesini döndürür.
        """
        if directory_path is None:
            directory_path = Directory.get_default_directory()

        directory = Directory.get_or_create_directory(directory_path)

        return FileRecord.objects.filter(directory=directory).values('filename', 'size')

