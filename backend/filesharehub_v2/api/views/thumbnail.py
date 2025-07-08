# backend/filesharehub_v2/api/views/thumbnail.py
import os
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from loguru import logger
from django.conf import settings
from django.core.exceptions import PermissionDenied
from filesharehub_v2.api.permissions import ReadOnlyPermission
from filesharehub_v2.models.filerecord import FileRecord
from filesharehub_v2.utils.cache import get_cached_thumbnail
from filesharehub_v2.tasks.generate_thumbnail import generate_thumbnail
from filesharehub_v2.utils.rules import is_safe_path
from celery.result import AsyncResult
from django.core.cache import cache

class ThumbnailView(APIView):
    permission_classes = [IsAuthenticated, ReadOnlyPermission]

    def get(self, request, file_id):
        logger.error(f"Thumbnail isteği: file_id={file_id}")

        try:
            file = FileRecord.objects.get(file_id=file_id)
        except FileRecord.DoesNotExist:
            logger.error(f"file_id={file_id} bulunamadı")
            raise Http404("Dosya bulunamadı.")

        if not file.is_image:
            logger.error(f"file_id={file_id} görsel dosya değil")
            raise Http404("Görsel dosya değil.")

        abs_path = os.path.join(settings.NETWORK_FOLDER_PATH, file.full_path)
        try:
            is_safe_path(settings.NETWORK_FOLDER_PATH, abs_path)
        except PermissionDenied as e:
            logger.error(f"Güvenlik hatası, file_id={file_id}, hata: {e}")
            raise Http404("Geçersiz dosya yolu.")

        # 1. Adım: Veritabanı path'i kontrol et
        if file.thumbnail_path and os.path.exists(os.path.join(settings.MEDIA_ROOT, file.thumbnail_path)):
            abs_thumb_path = os.path.join(settings.MEDIA_ROOT, file.thumbnail_path)
            return FileResponse(
                open(abs_thumb_path, "rb"),
                content_type="image/jpeg",
                headers={"Cache-Control": "max-age=86400"}
            )

        # 2. Adım: Redis cache kontrolü
        cached_thumb = get_cached_thumbnail(abs_path)
        if cached_thumb and os.path.exists(cached_thumb):
            return FileResponse(
                open(cached_thumb, "rb"),
                content_type="image/jpeg",
                headers={"Cache-Control": "max-age=86400"}
            )

        # 3. Adım: Celery görev durumunu kontrol et
        task_key = f"thumbnail_task:{file_id}"
        task_id = cache.get(task_key)
        if task_id:
            task = AsyncResult(task_id)
            if task.state in ['PENDING', 'STARTED']:
                logger.error(f"Thumbnail görevi devam ediyor: file_id={file_id}, task_id={task_id}")
                return Response(
                    {
                        "message": "Thumbnail üretiliyor, lütfen tekrar deneyin.",
                        "file_id": file_id,
                        "retry_after": 30,  # 15'ten 20'ye artırıldı
                    },
                    status=202,
                    headers={"Retry-After": "30"}
                )
            elif task.state == 'SUCCESS':
                file.refresh_from_db()
                if file.thumbnail_path and os.path.exists(os.path.join(settings.MEDIA_ROOT, file.thumbnail_path)):
                    abs_thumb_path = os.path.join(settings.MEDIA_ROOT, file.thumbnail_path)
                    return FileResponse(
                        open(abs_thumb_path, "rb"),
                        content_type="image/jpeg",
                        headers={"Cache-Control": "max-age=86400"}
                    )
                cache.delete(task_key)
            else:
                cache.delete(task_key)

        # 4. Adım: Thumbnail üretimi başlat
        logger.error(f"Thumbnail görevi başlatılıyor: file_id={file_id}")
        task = generate_thumbnail.delay(file.file_id)
        cache.set(task_key, task.id, timeout=300)  # 5 dakika sakla

        return Response(
            {
                "message": "Thumbnail üretiliyor, lütfen 30 saniye sonra tekrar deneyin.",
                "file_id": file_id,
                "retry_after": 30,
            },
            status=202,
            headers={"Retry-After": "30"}
        )