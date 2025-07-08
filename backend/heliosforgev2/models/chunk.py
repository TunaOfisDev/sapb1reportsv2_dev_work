# backend/heliosforgev2/models/chunk.py

from django.db import models
from heliosforgev2.models.document import Document

class Chunk(models.Model):
    """
    PDF'ten çıkarılan anlamlı metin bloklarını (başlık, paragraf, bölüm vs.) temsil eder.
    Her chunk bir belgeye (Document) ve belirli bir sayfaya aittir.
    """

    id = models.AutoField(primary_key=True)
    chunk_id = models.CharField(max_length=64, unique=True, help_text="DOC001-PAGE003-CHUNK007 gibi benzersiz ID")
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    page_number = models.PositiveIntegerField(help_text="Bu chunk'ın bulunduğu sayfa")
    section_title = models.CharField(max_length=255, null=True, blank=True, help_text="Chunk başlığı (varsa)")
    content = models.TextField(help_text="Chunk içinde yer alan metin içeriği")
    
    # Koordinat bilgisi (PDF'teki konumu temsil eder)
    left_x = models.FloatField()
    bottom_y = models.FloatField()
    right_x = models.FloatField()
    top_y = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chunk_id} (Page {self.page_number})"

    class Meta:
        verbose_name = "Chunk"
        verbose_name_plural = "Chunks"
        ordering = ["document", "page_number", "chunk_id"]
