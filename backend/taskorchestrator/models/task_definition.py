# backend/taskorchestrator/models/task_definition.py

from django.db import models

class TaskDefinition(models.Model):
    """
    Celery görevlerinin tanımlayıcı modelidir.
    Fonksiyon yolunu (Python import path) ve açıklamasını içerir.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Görev adı (örn: export_customer_balance)")
    function_path = models.CharField(
        max_length=255,
        help_text="Görev fonksiyonunun Python import yolu (örn: reports.tasks.export_balance)"
    )
    description = models.TextField(blank=True, help_text="Görevin ne yaptığına dair açıklama")
    is_active = models.BooleanField(default=True, help_text="Bu görev planlamaya açık mı?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Görev Tanımı"
        verbose_name_plural = "Görev Tanımları"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({'Aktif' if self.is_active else 'Pasif'})"
