# backend/taskorchestrator/models/scheduled_task.py

from django.db import models
from django_celery_beat.models import CrontabSchedule
from taskorchestrator.models.task_definition import TaskDefinition

class ScheduledTask(models.Model):
    """
    Sistemde çalışacak görevlerin zamanlamasını, parametrelerini ve aktiflik durumunu içerir.
    Celery Beat ile senkronize edilerek görev kuyruğuna yazılır.
    """
    name = models.CharField(max_length=150, unique=True, help_text="Görevin kolay tanınabilir adı")
    task = models.ForeignKey(TaskDefinition, on_delete=models.CASCADE, related_name="scheduled_tasks")
    crontab = models.ForeignKey(CrontabSchedule, on_delete=models.CASCADE)
    parameters = models.JSONField(default=dict, blank=True, help_text="Göreve gönderilecek parametreler")
    enabled = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Sistem yöneticisi notları")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-enabled", "name"]
        verbose_name = "Zamanlanmış Görev"
        verbose_name_plural = "Zamanlanmış Görevler"

    def __str__(self):
        return f"{self.name} | {self.task.name} ({'Aktif' if self.enabled else 'Pasif'})"
