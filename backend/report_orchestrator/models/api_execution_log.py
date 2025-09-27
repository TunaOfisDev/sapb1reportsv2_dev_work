# backend/report_orchestrator/models/api_execution_log.py

from django.db import models
from django.utils.timezone import now
from .api_report_model import APIReportModel


class APIExecutionLog(models.Model):
    """
    Her API raporunun günlük çalışma kaydını tutar.
    Hangi rapor ne zaman çalıştı, başarılı mıydı, hata verdiyse neydi gibi bilgileri içerir.
    """

    STATUS_CHOICES = [
        ('SUCCESS', 'Başarılı'),
        ('FAILED', 'Hatalı'),
    ]

    api = models.ForeignKey(
        APIReportModel,
        on_delete=models.CASCADE,
        related_name='execution_logs',
        help_text="Çalıştırılan raporun referansı"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SUCCESS',
        help_text="Raporun çalıştırma sonucu"
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Hata oluştuysa hata mesajı"
    )

    run_date = models.DateField(
        default=now,
        help_text="Raporun çalıştığı tarih (günlük özet için)"
    )

    run_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Çalıştırma anı (tam timestamp)"
    )

    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="İşlem süresi (isteğe bağlı performans ölçümü için)"
    )

    class Meta:
        verbose_name = "API Rapor Çalışma Kaydı"
        verbose_name_plural = "API Rapor Çalışma Kayıtları"
        ordering = ['-run_time']

    def __str__(self):
        return f"{self.api.api_name} | {self.status} @ {self.run_time.strftime('%Y-%m-%d %H:%M:%S')}"

