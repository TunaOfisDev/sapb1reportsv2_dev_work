# backend/heliosforge/models/document.py

from django.db import models
from django.utils import timezone


class Document(models.Model):
    DOC_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('xlsx', 'XLSX'),
        ('vtt', 'Video Subtitle'),
        ('txt', 'Plain Text'),
    ]

    title = models.CharField(max_length=255, help_text="Belgenin kısa başlığı")
    description = models.TextField(blank=True, help_text="İsteğe bağlı açıklama")
    file = models.FileField(upload_to='heliosforge/docs/', help_text="Yüklenen belge dosyası")
    doc_type = models.CharField(max_length=10, choices=DOC_TYPES, help_text="Belge türü")
    tags = models.JSONField(blank=True, null=True, help_text="Etiket listesi (isteğe bağlı)")
    
    uploaded_at = models.DateTimeField(default=timezone.now)
    is_chunked = models.BooleanField(default=False, help_text="Parçalanmış mı?")
    is_embedded = models.BooleanField(default=False, help_text="Embedding işlemi tamamlandı mı?")
    chunk_count = models.PositiveIntegerField(default=0, help_text="Oluşturulan chunk sayısı")

    source_url = models.URLField(blank=True, null=True, help_text="Varsa YouTube veya dış kaynak bağlantısı")

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Eğitim Belgesi"
        verbose_name_plural = "Eğitim Belgeleri"

    def __str__(self):
        return f"{self.title} ({self.doc_type})"

    def filename(self):
        return self.file.name.split('/')[-1]

    def extension(self):
        return self.filename().split('.')[-1].lower()
