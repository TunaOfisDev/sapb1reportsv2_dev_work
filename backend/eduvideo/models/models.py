# backend/eduvideo/models.py
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class EduVideo(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # description alanı boş olabilir
    video_url = models.URLField(unique=True)
    thumbnail_url = models.URLField() 
    published_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # YouTube API'den gelen verilerle eşleşen bir kayıt varsa güncelle
        if not self.pk and EduVideo.objects.filter(video_url=self.video_url).exists():
            existing_video = EduVideo.objects.get(video_url=self.video_url)
            existing_video.title = self.title
            existing_video.description = self.description
            existing_video.thumbnail_url = self.thumbnail_url  # thumbnail_url alanını da güncelle
            existing_video.published_at = self.published_at
            super(EduVideo, existing_video).save(*args, **kwargs)
        else:
            # Yeni kayıt oluştur
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title
