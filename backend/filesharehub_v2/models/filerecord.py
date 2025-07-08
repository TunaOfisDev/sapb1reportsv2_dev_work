# backend/filesharehub_v2/models/filerecord.py
import os
import hashlib
from django.db import models
from django.utils import timezone
from .base import TimeStampedModel, NamedModel


class FileRecord(TimeStampedModel, NamedModel):
    """
    Ağ dizinindeki bir dosya veya klasörü temsil eder.
    """
    file_id = models.BigIntegerField(editable=False, unique=True, db_index=True)
    path = models.TextField(help_text="Göreli dizin yoludur.")
    is_dir = models.BooleanField(default=False)
    size = models.BigIntegerField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    ext = models.CharField(max_length=10, blank=True)
    is_image = models.BooleanField(default=False)
    thumbnail_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("path", "name")
        ordering = ["name"]
    
    
    def __str__(self):
        return f"{'[DIR]' if self.is_dir else '[FILE]'} {self.path}/{self.name}"

    @property
    def full_path(self):
        return os.path.join(self.path, self.name)

  
    @staticmethod
    def compute_id(rel_path: str) -> int:
        """
        Göreli yol (örnek: KATALOG2023/banko1.jpg) üzerinden deterministik ID üretir.
        """
        normalized = rel_path.replace("\\", "/").strip("/")
        return int(hashlib.sha1(normalized.encode("utf-8")).hexdigest(), 16) % (10**9)


    def save(self, *args, **kwargs):
        if self.modified and timezone.is_naive(self.modified):
            self.modified = timezone.make_aware(self.modified)
        super().save(*args, **kwargs)