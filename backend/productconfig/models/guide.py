# backend/productconfig/models/guide.py
from django.db import models
from ..models.base import BaseModel

class Guide(BaseModel):
    """
    Kullanıcılar için ürün yapılandırma süreçlerine yönelik kılavuz içeriği sağlayan model.
    """
    title = models.CharField(max_length=255, verbose_name="Başlık")
    description = models.TextField(verbose_name="Amaci", help_text="Kılavuzun detaylı açıklaması.")
    steps = models.TextField(verbose_name="Islem Adımlari", help_text="Adım adım talimatlar. Markdown destekler.")
    category = models.CharField(
        max_length=100, verbose_name="Model", 
        help_text="Kılavuzun ait olduğu model yapisi. Örneğin: Marka, Ürün Grupları."
    )
    is_visible = models.BooleanField(default=True, verbose_name="Görünür mü?", help_text="Kılavuzun aktif olarak gösterilip gösterilmeyeceğini belirler.")

    class Meta:
        verbose_name = "Kılavuz"
        verbose_name_plural = "Kılavuzlar"
        ordering = ['id']

    def __str__(self):
        return self.title
