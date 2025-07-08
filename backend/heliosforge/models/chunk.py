# backend/heliosforge/models/chunk.py

from django.db import models
from .document import Document


class Chunk(models.Model):
    """
    Her belge parçası için içerik, konum, embedding durumu vb. bilgileri saklar.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.PositiveIntegerField(help_text="Belge içindeki sıra numarası")
    content = models.TextField(help_text="Parçalanmış ham metin içeriği")
    token_count = models.IntegerField(default=0, help_text="Token sayısı (isteğe bağlı)")
    
    # zaman/dakika referansı: video chunk'lar için
    start_time = models.CharField(max_length=20, blank=True, null=True, help_text="Başlangıç zamanı (ör. 00:03:45)")
    end_time = models.CharField(max_length=20, blank=True, null=True, help_text="Bitiş zamanı")

    # embedding işlemi ile ilişkili
    is_embedded = models.BooleanField(default=False)
    embedding_model = models.CharField(max_length=128, blank=True, null=True)
    embedding_vector_id = models.CharField(max_length=128, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('document', 'chunk_index')
        ordering = ['document', 'chunk_index']

    def __str__(self):
        return f"{self.document.source_name} [Chunk {self.chunk_index}]"
