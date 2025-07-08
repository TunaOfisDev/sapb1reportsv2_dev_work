# backend/crmblog/models/models.py
from authcentral.models import CustomUser
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Status(models.IntegerChoices):
    DRAFT = 0, "Taslak"
    PUBLISHED = 1, "Yayınla"
    ARCHIVED = 2, "Arşiv"

class Post(BaseModel):
    task_title = models.CharField(max_length=255, verbose_name="Görev Başlığı")
    project_name = models.CharField(max_length=255, blank=True, verbose_name="Proje Adı")
    deadline = models.DateField(default=timezone.now, verbose_name="Son Tarih")
    task_description = models.TextField(blank=True, verbose_name="Görev Açıklamaları")
    status = models.IntegerField(choices=Status.choices, default=Status.PUBLISHED)
    author = models.ForeignKey(CustomUser, related_name="blog_posts", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.task_title} - {self.project_name}"