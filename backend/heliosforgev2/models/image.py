# backend/heliosforgev2/models/image.py

from django.db import models
from heliosforgev2.models.document import Document
from heliosforgev2.models.chunk import Chunk

class Image(models.Model):
    """
    PDF içinden çıkarılan görselleri temsil eder.
    Her görsel bir belgeye (Document) ve opsiyonel olarak bir chunk'a (içerik bloğu) bağlanabilir.
    """

    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="images")
    chunk = models.ForeignKey(Chunk, on_delete=models.SET_NULL, null=True, blank=True, related_name="images")

    file_name = models.CharField(max_length=255, help_text="Görsel dosya adı (örneğin: DOC001-PAGE002-IMG001.png)")
    file_path = models.TextField(help_text="Görselin sunucudaki tam dosya yolu")

    page_number = models.PositiveIntegerField(help_text="Görselin yer aldığı sayfa numarası")
    
    # Görselin konum bilgisi
    left_x = models.FloatField(null=True, blank=True)
    bottom_y = models.FloatField(null=True, blank=True)
    right_x = models.FloatField(null=True, blank=True)
    top_y = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} (Page {self.page_number})"

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ["document", "page_number", "file_name"]

